from kafka import KafkaConsumer
import json
import logging
import os
from dotenv import load_dotenv
from ..models.order import Order
from ..processor.order_processor import OrderProcessor
from ..excel.excel_generator import ExcelGenerator
import signal
import sys

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrderKafkaConsumer:
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
        self.topic = os.getenv('KAFKA_TOPIC', 'order.created')
        self.group_id = os.getenv('KAFKA_CONSUMER_GROUP', 'python-excel-group')
        
        self.processor = OrderProcessor()
        self.excel_generator = ExcelGenerator()
        
        self.consumer = None
        self.running = True
        
    def setup_consumer(self):
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None,
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000,
            max_poll_records=10
        )
        logger.info(f"Conectado ao Kafka: {self.bootstrap_servers}")
        logger.info(f"Ouvindo tópico: {self.topic}")
        
    def process_message(self, message):
        try:
            logger.info("="*50)
            logger.info("Mensagem recebida do Kafka")
            
            order_data = message.value
            order = Order.from_dict(order_data)
            
            logger.info(f"Pedido ID: {order.order_id}")
            logger.info(f"User ID: {order.user_id}")
            logger.info(f"Itens: {len(order.items)}")
            
            rows = order.to_csv_rows()
            
            logger.info("Processando com LLM...")
            processed_rows = self.processor.process_with_llm([{
                'order_id': order.order_id,
                'user_id': order.user_id,
                'items': [{
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'unit_price': item.price
                } for item in order.items],
                'order_total': order.total_amount,
                'occurred_at': order.occurred_at
            }])
            
            if processed_rows:
                excel_path = self.excel_generator.generate_excel(
                    processed_rows, 
                    order.order_id
                )
                logger.info(f"Excel salvo em: {excel_path}")
            else:
                logger.warning("Nenhuma linha gerada para o pedido")
            
            self.consumer.commit()
            logger.info("Mensagem processada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
    
    def run(self):
        self.setup_consumer()
        
        def signal_handler(sig, frame):
            logger.info("Encerrando consumidor...")
            self.running = False
            if self.consumer:
                self.consumer.close()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Consumidor iniciado. Aguardando mensagens...")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                self.process_message(message)
                
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
        finally:
            if self.consumer:
                self.consumer.close()

def main():
    consumer = OrderKafkaConsumer()
    consumer.run()

if __name__ == "__main__":
    main()