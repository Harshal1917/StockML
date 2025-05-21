from enum import Enum

class Position:
    def __init__(self, trade_id):
        self.trade_id = trade_id
        self.orders = {'buy': [], 'sell': []}
        # List to store callbacks
        self._callbacks = []

    def register_callback(self, callback):
        """Register a callback function"""
        self._callbacks.append(callback)
    
    # def unregister_callback(self, callback):
    #     """Unregister a callback function"""
    #     self._callbacks.remove(callback)
    
    def notify_callbacks(self, event_type, data):
        """Notify all registered callbacks with the given data"""
        for callback in self._callbacks:
            callback(event_type, data)

    def position_callback(self, event_type, data):
        """Callback method for position events"""
        if event_type == 'order_added':
            print(f"\nPosition received order added event:")
            print(f"Order: {data['order']}")
        elif event_type == 'order_modified':
            print(f"\nPosition received order modified event:")
            print(f"Order: {data['order']}")

    def add_order(self, order):
        """Add an order and notify callbacks"""
        self.orders[order.order_side].append(order)
        order.set_position(self)
        
        # Register position's callback to listen to order changes
        order.register_callback(self.position_callback)

        # Notify callbacks about the new order
        self.notify_callbacks('order_added', {
            'position': self,
            'order': order
        })

    def __str__(self):
        return f"Position(trade_id={self.trade_id}, orders={len(self.orders['buy']) + len(self.orders['sell'])})"


class Order:
    def __init__(self, trade_id, order_side):
        self.trade_id = trade_id
        self.order_side = order_side
        self.position = None
        self._callbacks = []

    def register_callback(self, callback):
        """Register a callback function"""
        self._callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """Unregister a callback function"""
        self._callbacks.remove(callback)
    
    def notify_callbacks(self, event_type, data):
        """Notify all registered callbacks with the given data"""
        for callback in self._callbacks:
            callback(event_type, data)

    def order_callback(self, event_type, data):
        """Callback method for order events"""
        if event_type == 'modified':
            print(f"\nOrder received modified event:")
            print(f"Modified data: {data}")

    def set_position(self, position):
        """Set the position reference"""
        self.position = position

        position.register_callback(self.order_callback)

    def modify_order(self):
        """Example method to trigger callbacks"""
        # Notify own callbacks
        self.notify_callbacks('modified', {
            'order': self,
            'status': 'modified'
        })
        
        # Notify position if available
        if self.position:
            self.position.notify_callbacks('order_modified', {
                'order': self
            })

    def __str__(self):
        return f"Order(trade_id={self.trade_id}, side={self.order_side})"


# Simple test to demonstrate callback flow
def main():
    # Create instances
    position = Position(trade_id=123)
    order = Order(trade_id=123, order_side='buy')
    
    # Register only position callbacks
    # position.register_callback(position.position_callback)

    order.modify_order()

    # Add order to position (triggers position callback and registers order callback)
    position.add_order(order)
    
    # Modify order (triggers both callbacks)
    order.modify_order()


if __name__ == "__main__":
    main()
