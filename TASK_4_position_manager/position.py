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

#DONE#TODO: orders_state change code draft-logic 

#DONE#TODO: modify_order change enums
#DONE#TODO:here call modify_order_settled_qty

#DONE#TODO: check modify_peding_qty function
#DONE#TODO: timestamps add in order{updated_at}

#DONE:#TODO: handle exception in modify_order_pending_qty

#DONO:TODO: make class settled_trade: {  entry_order_id: who first come, 
#                                   exit_order_id: who come for counter, 
#                                    entry_execute_timestemp, 
#                                   exit_execute_timestemp, 
#                                   qty, 
#                                   entry_price, exit_price,
#                                   profit/loss}


#DONE#TODO: can not add settled order in position

#DONE#                               average executed price,

#DONE#TODO: 315 self.price = None {  limit price, { intially_set} by deafult-zero
#DONE#                                            make modify_limit_price() function seperately
#DONE#                               trigger price=> make fucntion for it and set intially too by_default = 0}

#DONE#TODO: add price attribute {average execution price}

#TODO: database integration CRUD

#TODO: order expiry_type? (duration) 
#TODO: order_type?(variety , stop loss , tigger , normal)
#TODO: order_expiry_time
#TODO: product_type: (delivery , intraday, carry forward)

#TODO: at the time of craetion and modification add into db!!!!

from order_storage import Trades

db = Trades()

class SettledTrade:
    def __init__(
        self,
        entry_order_id,
        exit_order_id,
        entry_execute_timestamp,
        exit_execute_timestamp,
        qty,
        entry_price,
        exit_price,
        profit_loss
    ):
        self.entry_order_id = entry_order_id
        self.exit_order_id = exit_order_id
        self.entry_execute_timestamp = entry_execute_timestamp
        self.exit_execute_timestamp = exit_execute_timestamp
        self.qty = qty
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.profit_loss = profit_loss

    def __str__(self):
        return (
            f"SettledTrade(entry_order_id={self.entry_order_id}, "
            f"exit_order_id={self.exit_order_id}, "
            f"entry_execute_timestamp={self.entry_execute_timestamp}, "
            f"exit_execute_timestamp={self.exit_execute_timestamp}, "
            f"qty={self.qty}, "
            f"entry_price={self.entry_price}, "
            f"exit_price={self.exit_price}, "
            f"profit_loss={self.profit_loss})"
        )

from enum import Enum
from datetime import datetime

class Position:
    # Initialization
    def __init__(self, trade_id, poston_qty=0, symbol=None):
        self.trade_id = trade_id
        self.poston_qty = poston_qty
        self.symbol = symbol
        self.orders = {'buy': [], 'sell': []}
        self.settled_orders = {'buy': [], 'sell': []}
        self._callbacks = []
        self._last_position_qty = poston_qty  # Initialize _last_position_qty

        self.settled_trades = []  # <-- Add this line to store SettledTrade objects

    def print_settled_trades(self):
        print("\nSettled Trades:")
        for trade in self.settled_trades:
            print(trade)

    # Core Position Management
    def add_order(self, order):
        if not self.can_add_order(order):
            print(f"Order cannot be added to the position: {order}")
            return False
        
        if order.status == 'not_placed':
            print(f"Order is in not_placed state and cannot be processed: {order}")
            return False

        # Add this check to prevent settled orders from being added
        if order.status == 'settled':
            print(f"Cannot add settled order to position: {order}")
            return False

        print(f"Order can be added to the position: {order}")
        
        if order.order_side == 'buy':
            self.orders['buy'].append(order)
        elif order.order_side == 'sell':
            self.orders['sell'].append(order)
        
        if self.symbol is None:
            self.symbol = order.symbol
        
        order.set_position(self)
        self.counter_position(order)
        self.calculate_position_qty()
        order.register_callback(self.handle_order_event)
        
        self.notify_callbacks('order_added', {
            'position': self,
            'order': order
        })

        # order_doc = {
        #     "broker_order_id": order.order_id,
        #     "account_id": "YOUR_ACCOUNT_ID",
        #     "strategy_id": "YOUR_STRATEGY_ID",
        #     "trade_id": order.trade_id,
        #     "symbol": order.symbol,
        #     "order_side": order.order_side,
        #     "pending_qty": order.pending_qty,
        #     "executed_qty": order.executed_qty,
        #     "settled_qty": order.settled_qty,
        #     "net_qty": order.net_qty,
        #     "status": order.status,
        #     "average_executed_price": order.average_executed_price,
        #     "limit_price": order.limit_price,
        #     "trigger_price": order.trigger_price,
        #     "created_at": str(order.created_at),
        #     "updated_at": str(order.updated_at),
        # }
        # db.AddOrder(order_id=order.order_id, doc=order_doc)

    def counter_position(self, new_order):
        """Counter the position quantity based on the new order quantity."""
        if new_order.order_side == 'buy':
            queue = self.orders['sell']
        elif new_order.order_side == 'sell':
            queue = self.orders['buy']
        else:
            print("Invalid order side.")
            return

        remaining_qty = new_order.executed_qty - new_order.settled_qty
        
        for existing_order in queue[:]:
            if remaining_qty <= 0:
                break
            
            if existing_order.status in ['executed', 'partially_executed', 'partially_settled']:
                available_qty = existing_order.executed_qty - existing_order.settled_qty
                if available_qty <= 0:
                    continue

                counter_qty = min(available_qty, remaining_qty)
                
                if counter_qty > 0:

                    
                    # --- Create SettledTrade instance here ---
                    entry_order, exit_order = (existing_order, new_order) if existing_order.created_at <= new_order.created_at else (new_order, existing_order)
                    entry_price = entry_order.average_executed_price  # Changed from 
                    exit_price = exit_order.average_executed_price   # Changed from 
                    # If you don't have price attribute, you can use another field or set to None

                    # Calculate profit/loss (assuming buy-entry: (exit_price - entry_price) * qty, sell-entry: (entry_price - exit_price) * qty)
                    if entry_order.order_side == 'buy':
                        profit_loss = (exit_price - entry_price) * counter_qty if exit_price is not None and entry_price is not None else None
                    else:
                        profit_loss = (entry_price - exit_price) * counter_qty if exit_price is not None and entry_price is not None else None

                    settled_trade = SettledTrade(
                        entry_order_id=entry_order.order_id,
                        exit_order_id=exit_order.order_id,
                        entry_execute_timestamp=entry_order.updated_at,
                        exit_execute_timestamp=exit_order.updated_at,
                        qty=counter_qty,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        profit_loss=profit_loss
                    )
                    self.settled_trades.append(settled_trade)
                    # --- End SettledTrade creation ---

                    
                    # Use modify_order_settled_qty for both orders
                    existing_order.modify_order_settled_qty(existing_order.settled_qty + counter_qty, increment=False)
                    new_order.modify_order_settled_qty(new_order.settled_qty + counter_qty, increment=False)
                    remaining_qty -= counter_qty
                    
                    if existing_order.status == 'settled':
                        self.orders[existing_order.order_side].remove(existing_order)
                        self.settled_orders[existing_order.order_side].append(existing_order)
                    if new_order.status == 'settled':
                        self.orders[new_order.order_side].remove(new_order)
                        self.settled_orders[new_order.order_side].append(new_order)

    def calculate_position_qty(self):
        """Calculate position quantity based on net quantities of all orders"""
        position_qty = 0
        
        for order in self.orders['buy']:
            position_qty += (order.executed_qty - order.settled_qty)
        
        for order in self.orders['sell']:
            position_qty -= (order.executed_qty - order.settled_qty)
        
        if position_qty != self._last_position_qty:

            print(f"\nPosition({self.trade_id}) updated: qty changed {self._last_position_qty} -> {position_qty}")

            self.poston_qty = position_qty
            self._last_position_qty = position_qty
            
            self.notify_callbacks('position_updated', {
                'position': self
            })
        
        return position_qty

    def move_to_settled(self, order):
        """Move an order to settled_orders if it's fully settled"""
        if order.status == 'settled':
            if order.order_side == 'buy':
                if order in self.orders['buy']:
                    self.orders['buy'].remove(order)
                    self.settled_orders['buy'].append(order)
            elif order.order_side == 'sell':
                if order in self.orders['sell']:
                    self.orders['sell'].remove(order)
                    self.settled_orders['sell'].append(order)

    # Order Validation
    def can_add_order(self, order):
        """Check if the order can be added to this position based on trade_id and symbol."""
        return (
            self.trade_id == order.trade_id and 
            (self.symbol == order.symbol or self.symbol is None)
        )

    # Event Handling
    def handle_order_event(self, event_type, data):
        """Handle order events"""
        if event_type == 'order_executed_modified':
            print(f"\nPosition({self.trade_id}) received order event: {event_type}")
            print(f"Order: {data['order']}")
            self.counter_position(data['order'])
            self.calculate_position_qty()
        elif event_type == 'order_pending_modified':
            print(f"\nPosition({self.trade_id}) received order event: {event_type}")
            print(f"Order: {data['order']}")
            # Only update position quantity, no need to counter position
            # self.calculate_position_qty()
        elif event_type == 'order_settled_modified':
            print(f"\nPosition({self.trade_id}) received order event: {event_type}")
            print(f"Order: {data['order']}")
            # Only update position quantity, no need to counter position
            self.calculate_position_qty()
        

    # Callback Management
    def register_callback(self, callback):
        """Register a callback function"""
        self._callbacks.append(callback)

    def notify_callbacks(self, event_type, data):
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            callback(event_type, data)

    # Debugging & String Representation
    def debug_print_state(self):
        """Print detailed state of the position for debugging"""
        print("\nPosition State:")
        print(f"Trade ID: {self.trade_id}")
        print(f"Position Quantity: {self.poston_qty}")
        print(f"Symbol: {self.symbol}")
        
        print("\nActive Orders:")
        print("Buy Orders:")
        for order in self.orders['buy']:
            print(f"  - {order}")
        print("Sell Orders:")
        for order in self.orders['sell']:
            print(f"  - {order}")
            
        print("\nSettled Orders:")
        print("Buy Orders:")
        for order in self.settled_orders['buy']:
            print(f"  - {order}")
        print("Sell Orders:")
        for order in self.settled_orders['sell']:
            print(f"  - {order}")

    def __str__(self):
        """String representation of Position"""
        return f"Position(trade_id={self.trade_id}, qty={self.poston_qty}, symbol={self.symbol})"

class Order:
    # Initialization
    def __init__(self, trade_id, pending_qty, executed_qty, status, order_side, symbol, order_id=None, average_executed_price=0.0, limit_price=0.0, trigger_price=0.0):
        self.trade_id = trade_id
        self.pending_qty = pending_qty
        self.executed_qty = executed_qty
        self.status = status
        self.order_side = order_side
        self.symbol = symbol
        self.settled_qty = 0
        self.net_qty = executed_qty
        self.position = None

        self.average_executed_price = average_executed_price
        self.limit_price = limit_price
        self.trigger_price = trigger_price
        self._callbacks = []
        #auto-generate order_id
        self.order_id = order_id
        self.created_at = datetime.now()
        self.updated_at = self.created_at

        # Add to database when order is created
        order_doc = {
            "broker_order_id": self.order_id,
            "account_id": "YOUR_ACCOUNT_ID",
            "strategy_id": "YOUR_STRATEGY_ID",
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "order_side": self.order_side,
            "pending_qty": self.pending_qty,
            "executed_qty": self.executed_qty,
            "settled_qty": self.settled_qty,
            "net_qty": self.net_qty,
            "status": self.status,
            "average_executed_price": self.average_executed_price,
            "limit_price": self.limit_price,
            "trigger_price": self.trigger_price,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
        db.AddOrder(order_id=self.order_id, doc=order_doc)

    def modify_order_execute_qty(self, additional_executed_qty, price):
        """Execute quantity with price and update average executed price"""
        if self.pending_qty < additional_executed_qty:
            raise ValueError("Cannot execute more than pending quantity")
        
        # Use only net_qty (unsettled qty) for average price calculation
        # total_value = (self.executed_qty * self.average_executed_price) + (additional_executed_qty * price)
        # self.executed_qty += additional_executed_qty
        # self.average_executed_price = total_value / self.executed_qty
    
        # Calculate total value of unsettled qty
        unsettled_value = self.net_qty * self.average_executed_price
        new_total_qty = self.net_qty + additional_executed_qty
        new_total_value = unsettled_value + (additional_executed_qty * price)
        self.executed_qty += additional_executed_qty
        self.average_executed_price = new_total_value / new_total_qty if new_total_qty > 0 else 0.0
    
        self.pending_qty -= additional_executed_qty
        self.updated_at = datetime.now()
        self.update_net_qty()
        self.validate_status()
        self.updated_at = datetime.now()
        
        # Update in database when order is modified
        update_doc = {
            "pending_qty": self.pending_qty,
            "executed_qty": self.executed_qty,
            "average_executed_price": self.average_executed_price,
            "status": self.status,
            "updated_at": str(self.updated_at),
        }
        db.ModifyOrder(order_id=self.order_id, update_doc=update_doc)

        if self.position:
            self.notify_callbacks('order_executed_modified', {
                'order': self,
                'position': self.position
            })

    def modify_order_pending_qty(self, additional_pending_qty, price=None):
        """Add to the pending quantity of the order if current pending_qty > 0. Optionally update limit price."""
        if self.pending_qty <= 0:
            raise ValueError(f"Cannot add pending quantity: order {self.order_id} has no pending quantity left.")
        # if additional_pending_qty <= 0:
        #     raise ValueError("Additional pending quantity must be positive.")

        self.pending_qty += additional_pending_qty
        if price is not None:
            self.limit_price = float(price)
        self.validate_status()
        self.updated_at = datetime.now()

        # Update in database when order is modified
        update_doc = {
            "pending_qty": self.pending_qty,
            "limit_price": self.limit_price,
            "status": self.status,
            "updated_at": str(self.updated_at),
        }
        db.ModifyOrder(order_id=self.order_id, update_doc=update_doc)

        if self.position:
            self.notify_callbacks('order_pending_modified', {
                'order': self,
                'position': self.position
            })
        return True

    def modify_limit_price(self, new_limit_price):
        """Modify the limit price of the order."""
        if not isinstance(new_limit_price, (int, float)):
            raise ValueError("Limit price must be a number.")
        if new_limit_price < 0:
            raise ValueError("Limit price cannot be negative.")
        self.limit_price = float(new_limit_price)
        self.updated_at = datetime.now()
        print(f"Order {self.order_id} limit price updated to: {self.limit_price}")
        # Optionally, notify callbacks if needed
        # self.notify_callbacks('order_limit_price_modified', {'order': self})

    def modify_trigger_price(self, new_trigger_price):
        """Modify the trigger price of the order."""
        if not isinstance(new_trigger_price, (int, float)):
            raise ValueError("Trigger price must be a number.")
        if new_trigger_price < 0:
            raise ValueError("Trigger price cannot be negative.")
        self.trigger_price = float(new_trigger_price)
        self.updated_at = datetime.now()
        print(f"Order {self.order_id} trigger price updated to: {self.trigger_price}")
        # Optionally, notify callbacks if needed
        # self.notify_callbacks('order_trigger_price_modified', {'order': self})

    def modify_order_settled_qty(self, value, increment=False):
        """
        Modify the settled quantity of the order.
        If increment=True, add value to current settled_qty.
        If increment=False, set settled_qty to value.
        """
        if increment:
            new_settled_qty = self.settled_qty + value
        else:
            new_settled_qty = value

        if new_settled_qty < 0:
            raise ValueError("Settled quantity cannot be negative.")
        if new_settled_qty > self.executed_qty:
            raise ValueError("Settled quantity cannot exceed executed quantity.")

        self.settled_qty = new_settled_qty
        self.update_net_qty()
        self.validate_status()
        self.updated_at = datetime.now()

        # Update in database when order is modified
        update_doc = {
            "settled_qty": self.settled_qty,
            "net_qty": self.net_qty,
            "status": self.status,
            "updated_at": str(self.updated_at),
        }
        db.ModifyOrder(order_id=self.order_id, update_doc=update_doc)

        if self.position:
            self.notify_callbacks('order_settled_modified', {
                'order': self,
                'position': self.position
            })

    # Quantity Management
    def set_executed_qty(self, executed_qty):
        """Set the executed quantity of the order and update net quantity."""
        self.executed_qty = executed_qty
        self.update_net_qty()

    def set_settled_qty(self, settled_qty):
        """Set the settled quantity of the order and update net quantity."""
        self.settled_qty = settled_qty
        self.update_net_qty()

    def update_net_qty(self):
        """Update the net quantity based on executed and settled quantities."""
        self.net_qty = self.executed_qty - self.settled_qty

    # Status Management  
    def set_status(self, status):
        """Set the status of the order."""
        self.status = status

    def validate_status(self):
        """Validate and update order status based on quantities"""
        if self.pending_qty > 0 and self.executed_qty == 0:
            self.status = 'pending'
        elif self.pending_qty > 0 and (self.net_qty > 0 or (self.executed_qty > 0 and self.settled_qty > 0)):
            self.status = 'partially_executed'
        elif self.pending_qty == 0 and self.settled_qty == 0:
            self.status = 'executed'
        elif self.pending_qty == 0 and self.net_qty > 0 and self.settled_qty > 0:
            self.status = 'partially_settled'
        elif self.pending_qty == 0 and self.net_qty == 0 and self.executed_qty == self.settled_qty:
            self.status = 'settled'

    def validate_not_placed(self):
        """Validate if order can be in not_placed state"""
        if self.executed_qty > 0:
            raise ValueError("Not placed order cannot have executed quantity")
        if self.settled_qty > 0:
            raise ValueError("Not placed order cannot have settled quantity")
        if self.pending_qty <= 0:
            raise ValueError("Not placed order must have positive pending quantity")

    # Position Management
    def set_position(self, position):
        """Set position reference and register position callback"""
        self.position = position
        # Only register if not already registered
        # if self.handle_position_event not in position._callbacks:
        position.register_callback(self.handle_position_event)
        return True

    # Event Handling
    def handle_position_event(self, event_type, data):
        if event_type == 'position_updated':
            # Remove or comment out these lines:
            print(f"\nOrder({self.trade_id}) received position event: {event_type}")
            print(f"Position: {data['position']}")
            # pass
        elif event_type == 'order_added':
            order = data.get('order')
            if order is not None and order is self:
                print(f"\nOrder({self.trade_id}) received position event: {event_type}")
                print(f"Order Added: ID={order.order_id}, Side={order.order_side}, Qty={order.executed_qty}, Status={order.status}")
                print(f"Position: {data['position']}")

    # Callback Management
    def register_callback(self, callback):
        """Register a callback function"""
        self._callbacks.append(callback)

    def notify_callbacks(self, event_type, data):
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            callback(event_type, data)

        if self.status == 'not_placed':
            self.validate_not_placed()

    def add_callback(self, callback_type, callback):
        """Register a callback function for a specific callback type."""
        if callback_type in self._callbacks:
            self._callbacks[callback_type].append(callback)
        else:
            print(f"Unsupported callback type: {callback_type}")

    # String Representation
    def __str__(self):
        return (f"Order - Trade ID: {self.trade_id}, "
                f"Order ID: {self.order_id}, "
                f"Pending Qty: {self.pending_qty}, "
                f"Executed Qty: {self.executed_qty}, "
                f"Avg Price: {self.average_executed_price:.2f}, "  # Changed from Price
                f"Limit Price: {self.limit_price:.2f}, "
                f"Trigger Price: {self.trigger_price:.2f}, "
                f"Settled Qty: {self.settled_qty}, "
                f"Net Qty: {self.net_qty}, "
                f"Status: {self.status}, "
                f"Order Side: {self.order_side}, "
                f"Symbol: {self.symbol}, "
                # f"Price: {self.price}, "  # <-- Remove this line
                f"Created At: {self.created_at}, "  # <-- Show created_at
                f"Updated At: {self.updated_at}")   # <-- Show updated_at
