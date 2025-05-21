from enum import Enum

class CallbackType(Enum):
    POSITION_UPDATED = 1
    ORDER_ADDED = 2
    # Add additional callback types here as needed 
    # Example:
    # ORDER_UPDATED = 3
    # POSITION_UPDATED = 4
    # ORDER_SETTLED = 5
    # POSITION_SETTLED = 6

class CallbackMessage:
    def __init__(self, callback_type, data):
        self.callback_type = callback_type
        self.data = data

    def __str__(self):
        return f"CallbackMessage(type={self.callback_type.name}, data={self.data})"

# Callback Functions
def position_update_callback(message):
    position = message.data
    print("\n=== Position Update Callback ===")
    print(f"Position ID: {position.trade_id}")
    print(f"Position Quantity: {position.poston_qty}")
    print(f"Symbol: {position.symbol}")
    print("===============================\n")

def order_added_callback(message):
    data = message.data
    position = data['position']
    order = data['order']
    print("\n=== Order Added Callback ===")
    print(f"Position ID: {position.trade_id}")
    print(f"Order Side: {order.order_side}")
    print(f"Order Status: {order.status}")
    print(f"Order Qty: {order.executed_qty}")
    print("==========================\n")

def register_all_callbacks(position):
    """Register all necessary callbacks for the position."""
    position.add_callback(CallbackType.POSITION_UPDATED, position_update_callback)
    position.add_callback(CallbackType.ORDER_ADDED, order_added_callback) 