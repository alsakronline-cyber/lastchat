from typing import List, Dict, Optional

class JourneyHandler:
    """
    Manages the customer journey state, transitioning from Product Discovery (Chat)
    to Purchasing (Quotation).
    """
    def __init__(self):
        self.state = "BROWSING"
        self.cart: List[Dict] = []
    
    def add_item_to_quote(self, sku: str, name: str, qty: int = 1, price: float = 0.0):
        """Adds an item to the potential quotation."""
        self.cart.append({
            "sku": sku,
            "name": name,
            "qty": qty,
            "price": price
        })
        self.state = "QUOTING"
        
    def get_quote_items(self) -> List[Dict]:
        return self.cart
    
    def clear_quote(self):
        self.cart = []
        self.state = "BROWSING"

    def detect_intent(self, user_message: str) -> str:
        """
        Simple intent detection rule-base.
        """
        user_message = user_message.lower()
        if "quote" in user_message or "price" in user_message or "buy" in user_message:
            return "INTENT_PURCHASE"
        return "INTENT_INFO"
