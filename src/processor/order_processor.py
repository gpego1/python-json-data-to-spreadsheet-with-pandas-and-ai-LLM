import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderProcessor:
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("MODEL", "gpt-4o-mini")
        
    def process_with_llm(self, orders_data: List[Dict]) -> List[Dict]:
        logger.info(f"Processando {len(orders_data)} pedidos com LLM")
        
        orders_for_llm = []
        for order in orders_data:
            order_dict = {
                "order_id": order["order_id"],
                "user_id": order["user_id"],
                "items": []
            }
            for item in order.get("items", []):
                order_dict["items"].append({
                    "product_id": item.get("product_id"),
                    "quantity": item.get("quantity"),
                    "unit_price": item.get("unit_price")
                })
            orders_for_llm.append(order_dict)
        
        response_schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "orders_csv_data",
                "schema": {
                    "type": "object",
                    "properties": {
                        "rows": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "order_id": {"type": "integer"},
                                    "user_id": {"type": "integer"},
                                    "product_id": {"type": "integer"},
                                    "quantity": {"type": "integer"},
                                    "unit_price": {"type": "number"},
                                    "item_total": {"type": "number"},
                                    "order_total": {"type": "number"},
                                    "occurred_at": {"type": "string"}
                                },
                                "required": [
                                    "order_id", "user_id", "product_id",
                                    "quantity", "unit_price", "item_total",
                                    "order_total", "occurred_at"
                                ]
                            }
                        }
                    },
                    "required": ["rows"]
                }
            }
        }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format=response_schema,
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are a data formatter. Convert the order data into rows for CSV generation.
                        Each item in an order becomes a separate row.
                        Calculate item_total = quantity * unit_price for each row.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Convert these orders into CSV rows (one row per item):
                        
                        {json.dumps(orders_for_llm, indent=2)}
                        
                        Return the data in the specified JSON schema format.
                        """
                    }
                ]
            )
            
            content = response.choices[0].message.content
            logger.info("LLM processou os dados com sucesso")
            
            result = json.loads(content)
            return result.get("rows", [])
            
        except Exception as e:
            logger.error(f"Erro ao processar com LLM: {e}")
            return self._process_locally(orders_data)
    
    def _process_locally(self, orders_data: List[Dict]) -> List[Dict]:
        logger.info("Usando processamento local (fallback)")
        rows = []
        for order in orders_data:
            for item in order.get("items", []):
                rows.append({
                    "order_id": order["order_id"],
                    "user_id": order["user_id"],
                    "product_id": item.get("product_id"),
                    "quantity": item.get("quantity"),
                    "unit_price": item.get("unit_price"),
                    "item_total": item.get("quantity", 0) * item.get("unit_price", 0),
                    "order_total": order.get("order_total", 0),
                    "occurred_at": order.get("occurred_at", "")
                })
        return rows