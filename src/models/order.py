from dataclasses import dataclass
from typing import List, Optional
import json
from datetime import datetime

@dataclass
class OrderItem:
    product_id: int
    quantity: int
    price: float

    @classmethod
    def from_dict(cls, data):
        return cls(
            product_id=data.get('productId') or data.get('product_id'),
            quantity=data.get('quantity'),
            price=float(data.get('price',0))
        )
@dataclass
class Order:
    event_id: str
    order_id: int
    user_id: int
    user_email: str
    items: List[OrderItem]
    total_amount: float
    occurred_at: str
    
    @classmethod
    def from_dict(cls, data):
        items_data = data.get('items', [])
        items = [OrderItem.from_dict(item) for item in items_data]
        
        return cls(
            event_id=data.get('eventId') or data.get('event_id'),
            order_id=data.get('orderId') or data.get('order_id'),
            user_id=data.get('userId') or data.get('user_id'),
            user_email=data.get('userEmail') or data.get('user_email'),
            items=items,
            total_amount=float(data.get('totalAmount') or data.get('total_amount', 0)),
            occurred_at=data.get('occurredAt') or data.get('occurred_at')
        )
    
    def to_csv_rows(self):
        rows = []
        for item in self.items:
            rows.append({
                "order_id": self.order_id,
                "user_id": self.user_id,
                "user_email": self.user_email,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.price,
                "item_total": item.quantity * item.price,
                "order_total": self.total_amount,
                "occurred_at": self.occurred_at
            })
        return rows