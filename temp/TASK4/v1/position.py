# This program defines a Position and Order system for managing trades.
# 
# Order Statuses:
# - not_placed: The order is yet to be executed.
# - pending: The order is yet to be executed.
# - partially_executed: The order has been partially filled.
# - executed: The order has been fully filled.
# - partially_settled: The order has been partially matched and closed.
# - settled: The order has been fully matched and closed.
# - failed: The order could not be executed due to some error.
#
# Equation for net quantity:
# net_qty = executed_qty - settled_qty

#DONE#TODO:  pending->par_exe->exe->par_set->set, failed, cancled
#DONE#TODO:  pending_qty*
#DONE#TODO:  callback study

#DONE#TODO: enum pass for callback
#DONE#TODO: as a object with event enum

#DONE#TODO: muliple callbacks should be different for all objects

#DONE#TODO: stop-loss, take-profit, trailing-stop

#DONE#TODO: if order not affecting position then not require to call position callback
#DONE#TODO: position was plus even in sell order
#DONE#TODO: not_placed->pending->par_exe->exe->par_set->set, failed, cancled
#TODO: orders_state change code draft-logic 

from enum import Enum
from callbacks import CallbackType, CallbackMessage

class Position:
    def __init__(self, trade_id, poston_qty=0, symbol=None):
        self.trade_id = trade_id  # Unique identifier for the trade
        self.poston_qty = poston_qty  # Curre   nt quantity in the position
        self.symbol = symbol  # Symbol for the position
        self.orders = {'buy': [], 'sell': []}  # Dictionary to track added orders
        self.settled_orders = {'buy': [], 'sell': []}  # Dictionary to track settled orders
        self.callbacks = {callback_type: [] for callback_type in CallbackType}  # Callbacks categorized by type

    def add_callback(self, callback_type, callback):
        """Register a callback function for a specific callback type."""
        if callback_type in self.callbacks:
            self.callbacks[callback_type].append(callback)
        else:
            print(f"Unsupported callback type: {callback_type}")

    def handle_callback(self, callback_type, data=None):
        """Handle the callback by invoking the appropriate registered callbacks."""
        if callback_type == CallbackType.POSITION_UPDATED:
            message = CallbackMessage(callback_type, self)
        else:  # Order-related callbacks
            message = CallbackMessage(callback_type, {
                'position': self,
                'order': data
            })
        
        for callback in self.callbacks.get(callback_type, []):
            callback(message)

    def add_order(self, order):
        """Add an order to this position if the trade_id matches."""
        if not self.can_add_order(order):
            print(f"Order cannot be added to the position: {order}")
            return False

        # Don't process not_placed orders
        if order.status == 'not_placed':
            print(f"Order is in not_placed state and cannot be processed: {order}")
            return False

        print(f"Order can be added to the position: {order}")
        
        # Store initial position quantity for comparison
        initial_qty = self.poston_qty
        
        # Check for countering before adding the order
        self.counter_position(order)
        
        # If the order is not settled, update the position
        if order.status not in ['settled', 'partially_settled']:
            self.update_position(order.executed_qty, order.order_side)
        
        # Track the added order in the appropriate queue
        if order.order_side == 'buy':
            self.orders['buy'].append(order)
        elif order.order_side == 'sell':
            self.orders['sell'].append(order)
        
        # Set the symbol if it's not already set
        if self.symbol is None:
            self.symbol = order.symbol
        
        # Only trigger position callback if quantity changed
        if self.poston_qty != initial_qty:
            self.handle_callback(CallbackType.POSITION_UPDATED)
        
        # Notify order added callback
        self.handle_callback(CallbackType.ORDER_ADDED, order)
        return True

    def can_add_order(self, order):
        """Check if the order can be added to this position based on trade_id and symbol."""
        return self.trade_id == order.trade_id and (self.symbol == order.symbol or self.symbol is None)

    def update_position(self, executed_qty, order_side):
        """Update the position quantity based on the executed order quantity and side."""
        # For buy orders, add to position. For sell orders, subtract from position
        qty_change = executed_qty if order_side == 'buy' else -executed_qty
        self.poston_qty += qty_change
        # Notify callbacks after updating the position
        self.handle_callback(CallbackType.POSITION_UPDATED, self)

    def counter_position(self, new_order):
        """Counter the position quantity based on the new order quantity."""
        if new_order.order_side == 'buy':
            queue = self.orders['sell']
        elif new_order.order_side == 'sell':
            queue = self.orders['buy']
        else:
            print("Invalid order side.")
            return

        for existing_order in queue:
            if existing_order.status in ['executed', 'partially_executed']:
                # Determine how much can be countered
                counter_qty = min(existing_order.executed_qty - existing_order.settled_qty, 
                                new_order.executed_qty - new_order.settled_qty)
                
                if counter_qty > 0:
                    # Update quantities
                    existing_order.settled_qty += counter_qty
                    new_order.settled_qty += counter_qty
                    
                    # Update net quantities
                    existing_order.net_qty = existing_order.executed_qty - existing_order.settled_qty
                    new_order.net_qty = new_order.executed_qty - new_order.settled_qty

                    # Check if existing_order is fully settled
                    if existing_order.settled_qty == existing_order.executed_qty and existing_order.pending_qty == 0:
                        existing_order.status = 'settled'
                        if existing_order.order_side == 'buy':
                            self.settled_orders['buy'].append(existing_order.__dict__)
                        elif existing_order.order_side == 'sell':
                            self.settled_orders['sell'].append(existing_order.__dict__)
                    else:
                        existing_order.status = 'partially_settled' if existing_order.status == 'executed' else 'partially_executed'

                    # Check if new_order is fully settled
                    if new_order.settled_qty == new_order.executed_qty and new_order.pending_qty == 0:
                        new_order.status = 'settled'
                        if new_order.order_side == 'buy':
                            self.settled_orders['buy'].append(new_order.__dict__)
                        elif new_order.order_side == 'sell':
                            self.settled_orders['sell'].append(new_order.__dict__)
                    else:
                        new_order.status = 'partially_settled' if new_order.status == 'executed' else 'partially_executed'

                    print(f"[***Countered order***]: {existing_order} with new order: {new_order}")

                    # If the new order is settled, we can exit
                    if new_order.status == 'settled':
                        return

        # If no matching order is found
        print("No matching order found to counter.")

    def __str__(self):
        return (f"Position - Trade ID: {self.trade_id}, "
                f"Poston Qty: {self.poston_qty}, "
                f"Symbol: {self.symbol}, "
                f"Orders: {len(self.orders['buy']) + len(self.orders['sell'])}, "
                f"Settled Orders: {len(self.settled_orders['buy']) + len(self.settled_orders['sell'])}")


class Order:
    def __init__(self, trade_id, pending_qty, executed_qty, status, order_side, symbol):
        self.trade_id = trade_id  # Unique identifier for the trade
        self.pending_qty = pending_qty  # Quantity still pending
        self.executed_qty = executed_qty  # Quantity that has been executed
        self.status = status  # Status of the order (not_placed, pending, partially_executed, executed, partially_settled, settled, failed)
        self.order_side = order_side  # Side of the order (buy, sell)
        self.symbol = symbol  # Symbol for the order
        self.settled_qty = 0  # Quantity that has been settled
        self.net_qty = max(0, executed_qty - self.settled_qty)  # Net quantity (executed - settled)

        # Validate if order is not_placed
        if self.status == 'not_placed':
            self.validate_not_placed()

    def validate_not_placed(self):
        """Validate if order can be in not_placed state"""
        if self.executed_qty > 0:
            raise ValueError("Not placed order cannot have executed quantity")
        if self.settled_qty > 0:
            raise ValueError("Not placed order cannot have settled quantity")
        if self.pending_qty <= 0:
            raise ValueError("Not placed order must have positive pending quantity")
    
    #if broker want to change it to pending
    def place_order(self):
        """Transition order from not_placed to pending state"""
        if self.status != 'not_placed':
            raise ValueError(f"Can only place orders in not_placed state. Current state: {self.status}")
        
        self.status = 'pending'
        return True

    def set_executed_qty(self, executed_qty):
        """Set the executed quantity of the order and update net quantity."""
        self.executed_qty = executed_qty
        self.update_net_qty()

    def set_status(self, status):
        """Set the status of the order."""
        self.status = status

    def update_net_qty(self):
        """Update the net quantity based on executed and settled quantities."""
        self.net_qty = max(0, self.executed_qty - self.settled_qty)

    def set_settled_qty(self, settled_qty):
        """Set the settled quantity of the order and update net quantity."""
        self.settled_qty = settled_qty
        self.update_net_qty()

    def validate_status(self):
        """Validate the status of the order based on quantities."""
        if self.status == 'not_placed':
            # Not placed orders should only have pending quantity
            if self.executed_qty > 0 or self.settled_qty > 0:
                self.status = 'failed'
        elif self.pending_qty > 0 and self.executed_qty == 0:
            self.status = 'pending'
        elif self.pending_qty > 0 and self.executed_qty > 0:
            self.status = 'partially_executed'
        elif self.pending_qty == 0 and self.executed_qty > 0:
            self.status = 'executed'
        elif self.settled_qty > 0 and self.settled_qty < self.executed_qty:
            self.status = 'partially_settled'
        elif self.settled_qty == self.executed_qty and self.pending_qty == 0:
            self.status = 'settled'
        else:
            self.status = 'failed'

    def __str__(self):
        return (f"Order - Trade ID: {self.trade_id}, "
                f"Pending Qty: {self.pending_qty}, "
                f"Executed Qty: {self.executed_qty}, "
                f"Settled Qty: {self.settled_qty}, "
                f"Net Qty: {self.net_qty}, "
                f"Status: {self.status}, "
                f"Order Side: {self.order_side}, "
                f"Symbol: {self.symbol}")
    
    #edit_order
    # def set_pending_qty(self, pending_qty):
    #     """Set the pending quantity of the order."""
    #     self.pending_qty = pending_qty


