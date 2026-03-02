import os
import json
from dotenv import load_dotenv
from ..models.order import Order
from ..processor.order_processor import OrderProcessor
from ..excel.excel_generator import ExcelGenerator

load_dotenv()

def read_orders_json(caminho_arquivo):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        
        orders = []
        for pedido in dados.get("orders", []):
            order_data = {
                "eventId": f"manual-{pedido.get('id')}",
                "orderId": pedido.get("id"),
                "userId": pedido.get("user_id", 0),
                "userEmail": pedido.get("user_email", "unknown@email.com"),
                "items": [
                    {
                        "productId": produto.get("id") or produto.get("product_id"),
                        "quantity": produto.get("quantidade"),
                        "price": produto.get("preco")
                    }
                    for produto in pedido.get("produtos", [])
                ],
                "totalAmount": pedido.get("preco_total"),
                "occurredAt": pedido.get("created_at", "2024-01-01T00:00:00")
            }
            orders.append(Order.from_dict(order_data))
        
        return orders
    except FileNotFoundError:
        print("JSON file not found.")
    except json.JSONDecodeError:
        print("Fail to load JSON.")

def main():
    print("Processando pedidos via main.py")
    
    json_path = os.path.join(os.path.dirname(__file__), "../models/mock/orders.json")
    orders = read_orders_json(json_path)

    if not orders:
        raise Exception("No orders found.")
    
    print(f" Encontrados {len(orders)} pedidos")
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'order_id': order.order_id,
            'user_id': order.user_id,
            'items': [{
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': item.price
            } for item in order.items],
            'order_total': order.total_amount,
            'occurred_at': order.occurred_at
        })
    
    processor = OrderProcessor()
    excel_gen = ExcelGenerator(output_path="./output")
    
    print("Processando com LLM...")
    processed_rows = processor.process_with_llm(orders_data)
    
    if processed_rows:
        excel_path = excel_gen.generate_excel(processed_rows)
        print(f"Planilha gerada: {excel_path}")
    else:
        print("Nenhuma linha gerada")
    
    print("Processamento concluído!")

if __name__ == "__main__":
    main()