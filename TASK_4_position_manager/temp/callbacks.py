#TODO: inside position class @order_modified_callback, @order_added_callback

from enum import Enum

class CallbackType(Enum):
    POSITION_UPDATED = "position_updated"
    ORDER_ADDED = "order_added"
    ORDER_MODIFIED = "order_modified"
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

#inside position class
def order_modified_callback(message):
    """Callback function for order modification events"""
    data = message.data
    order = data['order']
    
    print("\n=== Order Modified Callback ===")
    print(f"Order Trade ID: {order.trade_id}")
    print(f"Order Side: {order.order_side}")
    print(f"Order Status: {order.status}")
    print(f"Pending Qty: {order.pending_qty}")
    print(f"Executed Qty: {order.executed_qty}")
    print(f"Settled Qty: {order.settled_qty}")
    
    # Only handle position-related operations if position exists
    if 'position' in data and data['position'] is not None:
        position = data['position']
        print(f"Position ID: {position.trade_id}")
        print(f"Position Quantity: {position.poston_qty}")
        # Counter the modified order through position
        position.counter_position(order)
    else:
        print("Order not associated with any position")
    
    print("============================\n")

def register_position_callbacks(position):
    """Register all callbacks for a position"""
    position.add_callback(CallbackType.POSITION_UPDATED, position_update_callback)
    position.add_callback(CallbackType.ORDER_ADDED, order_added_callback)
    # position.add_callback(CallbackType.ORDER_MODIFIED, position.order_modified_callback)

def register_order_callbacks(order):
    """Register all callbacks for an order"""

    order.add_callback(CallbackType.ORDER_MODIFIED, order_modified_callback) 