# This program defines a Position and Order system for managing trades.
# 
# Order Statuses:
# - failed: The order could not be executed due to some error.
# - not_placed: The order is yet to be executed.
# - pending: The order is yet to be executed.
# - partially_executed: The order has been partially filled.
# - executed: The order has been fully filled.
# - partially_settled: The order has been partially matched and closed.
# - settled: The order has been fully matched and closed.

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


#TODO: modify_order 
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
        
        # Track the added order in the appropriate queue
        if order.order_side == 'buy':
            self.orders['buy'].append(order)
        elif order.order_side == 'sell':
            self.orders['sell'].append(order)
        
        # Set the symbol if it's not already set
        if self.symbol is None:
            self.symbol = order.symbol
        
        # Recalculate position quantity
        self.calculate_position_qty()
        
        # Only trigger position callback if quantity changed
        if self.poston_qty != initial_qty:
            self.handle_callback(CallbackType.POSITION_UPDATED)
        
        # Notify order added callback
        self.handle_callback(CallbackType.ORDER_ADDED, order)
        order.position = self  # Set the position reference
        return True

    def can_add_order(self, order):
        """Check if the order can be added to this position based on trade_id and symbol."""
        return self.trade_id == order.trade_id and (self.symbol == order.symbol or self.symbol is None)

    def update_position(self, executed_qty, order_side):
        """Update the position quantity based on the executed order quantity and side."""
        # Instead of directly updating, recalculate based on all orders
        self.poston_qty = self.calculate_position_qty()
        # Notify callbacks after updating the position
        self.handle_callback(CallbackType.POSITION_UPDATED, self)

    def calculate_position_qty(self):
        """Calculate position quantity based on net quantities of all orders"""
        position_qty = 0
        
        # Add buy order net quantities
        for order in self.orders['buy']:
            position_qty += (order.executed_qty - order.settled_qty)
        
        # Subtract sell order net quantities
        for order in self.orders['sell']:
            position_qty -= (order.executed_qty - order.settled_qty)
        
        return position_qty

    def counter_position(self, new_order):
        """Counter the position quantity based on the new order quantity."""
        if new_order.order_side == 'buy':
            queue = self.orders['sell']
        elif new_order.order_side == 'sell':
            queue = self.orders['buy']
        else:
            print("Invalid order side.")
            return

        # Sort orders by execution time only (earlier first)
        sorted_queue = sorted(queue, key=lambda x: id(x))

        for existing_order in sorted_queue:
            if existing_order.status in ['executed', 'partially_executed', 'partially_settled']:
                # Skip if no available quantity to counter
                available_qty = existing_order.executed_qty - existing_order.settled_qty
                if available_qty <= 0:
                    continue

                # Determine how much can be countered
                counter_qty = min(
                    available_qty,
                    new_order.executed_qty - new_order.settled_qty
                )
                
                if counter_qty > 0:
                    print(f"Countering {counter_qty} qty between {existing_order} and {new_order}")
                    
                    # Update quantities
                    existing_order.settled_qty += counter_qty
                    new_order.settled_qty += counter_qty
                    
                    # Update net quantities
                    existing_order.net_qty = existing_order.executed_qty - existing_order.settled_qty
                    new_order.net_qty = new_order.executed_qty - new_order.settled_qty

                    # Update statuses
                    if existing_order.settled_qty == existing_order.executed_qty:
                        if existing_order.pending_qty == 0:
                            existing_order.status = 'settled'
                            # Move to settled orders
                            self.move_to_settled_orders(existing_order)
                        else:
                            existing_order.status = 'partially_settled'

                    if new_order.settled_qty == new_order.executed_qty:
                        if new_order.pending_qty == 0:
                            new_order.status = 'settled'
                            # Move to settled orders
                            self.move_to_settled_orders(new_order)
                        else:
                            new_order.status = 'partially_executed'

                    # Recalculate position quantity
                    self.poston_qty = self.calculate_position_qty()

                    print(f"[***Countered order***]: {existing_order} with new order: {new_order}")

                    # If new order is fully settled, stop countering
                    if new_order.settled_qty == new_order.executed_qty:
                        break

    def try_counter_orders(self, modified_order):
        """Try to match and settle counter orders for the modified order"""
        counter_side = 'sell' if modified_order.order_side == 'buy' else 'buy'
        
        # Look through orders on the opposite side
        for order in self.orders[counter_side]:
            if order.status in ['executed', 'partially_executed']:
                # Calculate how much can be settled
                available_qty = min(
                    modified_order.executed_qty - modified_order.settled_qty,
                    order.executed_qty - order.settled_qty
                )
                
                if available_qty > 0:
                    # Update settled quantities for both orders
                    modified_order.settled_qty += available_qty
                    order.settled_qty += available_qty
                    
                    # Update order statuses
                    modified_order.validate_status()
                    order.validate_status()
                    
                    # Move settled orders to settled_orders if fully settled
                    if modified_order.status == 'settled':
                        self.move_to_settled(modified_order)
                    if order.status == 'settled':
                        self.move_to_settled(order)

    def __str__(self):
        return (f"Position - Trade ID: {self.trade_id}, "
                f"Poston Qty: {self.poston_qty}, "
                f"Symbol: {self.symbol}, "
                f"Orders: {len(self.orders['buy']) + len(self.orders['sell'])}, "
                f"Settled Orders: {len(self.settled_orders['buy']) + len(self.settled_orders['sell'])}")

    def create_modification_order(self, original_order, additional_executed_qty):
        """Create a new modification order based on the original order"""
        mod_order = Order(
            trade_id=original_order.trade_id,
            pending_qty=original_order.pending_qty - additional_executed_qty,
            executed_qty=additional_executed_qty,
            status='partially_executed' if original_order.pending_qty > additional_executed_qty else 'executed',
            order_side=original_order.order_side,
            symbol=original_order.symbol
        )
        
        # Update original order's pending quantity
        original_order.pending_qty -= additional_executed_qty
        original_order.validate_status()
        
        # Add modification order to position
        self.add_order(mod_order)
        
        return mod_order

    def move_to_settled_orders(self, order):
        """Move an order to settled orders if it exists in active orders"""
        if order in self.orders[order.order_side]:
            self.settled_orders[order.order_side].append(order)
            self.orders[order.order_side].remove(order)

    def modify_order(self, order, additional_executed_qty):
        """Modify order and handle countering"""
        # Update the order quantities
        order.pending_qty -= additional_executed_qty
        order.executed_qty += additional_executed_qty
        order.update_net_qty()
        order.validate_status()
        
        # Counter the modified order
        self.counter_position(order)
        
        # Update position quantity
        self.poston_qty = self.calculate_position_qty()


class Order:
    def __init__(self, trade_id, pending_qty, executed_qty, status, order_side, symbol):
        self.trade_id = trade_id
        self.pending_qty = pending_qty
        self.executed_qty = executed_qty
        self.status = status
        self.order_side = order_side
        self.symbol = symbol
        self.settled_qty = 0
        self.net_qty = executed_qty  # Initial net_qty is equal to executed_qty
        self.position = None  # Reference to containing position

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
        self.net_qty = self.executed_qty - self.settled_qty  # Remove max(0, ...) to allow proper calculation

    def set_settled_qty(self, settled_qty):
        """Set the settled quantity of the order and update net quantity."""
        self.settled_qty = settled_qty
        self.update_net_qty()

    def validate_status(self):
        """Validate and update order status based on quantities"""
        if self.executed_qty == 0:
            self.status = 'pending'
        elif self.pending_qty > 0 and self.executed_qty > 0:
            self.status = 'partially_executed'
        elif self.pending_qty == 0 and self.executed_qty > 0:
            if self.settled_qty == self.executed_qty:
                self.status = 'settled'
            elif self.settled_qty > 0:
                self.status = 'partially_settled'
            else:
                self.status = 'executed'

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

    def modify_order_execute_qty(self, additional_executed_qty):
        """Modify order's executed quantity and try counter orders"""
        if self.pending_qty < additional_executed_qty:
            raise ValueError("Cannot execute more than the pending quantity.")
        
        # Update the original order's quantities
        self.pending_qty -= additional_executed_qty
        self.executed_qty += additional_executed_qty
        self.update_net_qty()
        self.validate_status()
        
        # Try to counter with other orders if in a position
        if hasattr(self, 'position'):
            self.position.counter_position(self)
        
        return self


