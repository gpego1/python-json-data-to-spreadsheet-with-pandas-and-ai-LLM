from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import pandas as pd

load_dotenv()

client_openai = OpenAI(
    base_url = os.getenv("BASE_URL"),
    api_key = os.getenv("OPENAI_API_KEY")
)

def read_orders_json(caminho_arquivo):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        rows = []

        for pedido in dados.get("orders", []):
            pedido_id = pedido.get("id")

            for produto in pedido.get("produtos", []):
                rows.append({
                    "order_id": pedido_id,
                    "product_name": produto.get("nome"),
                    "quantity": produto.get("quantidade"),
                    "unit_price": produto.get("preco"),
                    "total_order_price": pedido.get("preco_total")
                })

        return rows
    except FileNotFoundError:
        print("JSON file not found.")
    except json.JSONDecodeError:
        print("Fail to load JSON.")

orders = read_orders_json("./src/models/mock/orders.json")
if not orders:
    raise Exception("No orders found.")

response = client_openai.chat.completions.create(
    model=os.getenv("MODEL"),
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "orders_csv",
            "schema": {
                "type": "object",
                "properties": {
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "number"},
                                "product_name": {"type": "string"},
                                "quantity": {"type": "number"},
                                "unit_price": {"type": "number"},
                                "total_order_price": {"type": "number"}
                            },
                            "required": [
                                "order_id",
                                "product_name",
                                "quantity",
                                "unit_price",
                                "total_order_price"
                            ]
                        }
                    }
                },
                "required": ["rows"]
            }
        }
    },
    messages=[
        {
            "role": "system",
            "content": "Return the order data structured for CSV generation."
        },
        {
            "role": "user",
            "content": f"""
    Convert these orders into rows (one row per item):

    {json.dumps(orders, indent=2)}
    """
        }
    ]
)
content = response.choices[0].message.content
print(content)

data = json.loads(content)
df = pd.DataFrame(data["rows"])

with pd.ExcelWriter("orders.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Orders", index = False)
    workSheet = writer.sheets["Orders"]
    workSheet.freeze_panes = "A2"
    
print("XLSX successfully generated.")
