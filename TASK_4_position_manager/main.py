from position import Position, Order
import pandas as pd
from copy import deepcopy
import os

#DONE#TODO: add order_ID in order

def log_test_case(position_before, position_after, orders_before, orders_after, modified_orders=None, event_sequence=None):
    """Log test case to Excel with before and after states"""
    excel_file = 'position_order_test_cases.xlsx'
    next_case_id = get_next_case_id(excel_file)
    timeline = []
    
    # Add BEFORE position
    timeline.append({
        'Case ID': next_case_id,
        'State: before/after': 'before',
        'Record Type: order/position': 'POSITION',
        'Trade ID': position_before.trade_id,
        'Position Qty': position_before.poston_qty,
        'Symbol': position_before.symbol if position_before.symbol else 'None',
        'Orders Count': len(position_before.orders['buy']) + len(position_before.orders['sell']),
        'Settled Orders': len(position_before.settled_orders['buy']) + len(position_before.settled_orders['sell']),
        'Pending Qty': '-',
        'Executed Qty': '-',
        'Settled Qty': '-',
        'Net Qty': '-',
        'Status': '-',
        'Order Side': '-'
    })
    
    # Use event_sequence to maintain order
    for event in event_sequence:
        if '_modification' in event:
            order_name = event.replace('_modification', '')
            mod_order = modified_orders[order_name]
            final_order = orders_after[order_name]
            additional_executed_qty = final_order.executed_qty - mod_order.executed_qty
            
            timeline.append({
                'Case ID': '',
                'State: before/after': '',
                'Record Type: order/position': event,
                'Trade ID': mod_order.trade_id,
                'Position Qty': '-',
                'Symbol': mod_order.symbol,
                'Orders Count': '-',
                'Settled Orders': '-',
                'Pending Qty': mod_order.pending_qty - additional_executed_qty,
                'Executed Qty': mod_order.executed_qty + additional_executed_qty,
                'Settled Qty': mod_order.settled_qty,
                'Net Qty': (mod_order.executed_qty + additional_executed_qty) - mod_order.settled_qty,
                'Status': final_order.status,
                'Order Side': mod_order.order_side
            })
        elif '_pending_modified' in event:
            order_name = event.replace('_pending_modified', '')
            order_before = orders_before[order_name]
            order_after = orders_after[order_name]
            timeline.append({
                'Case ID': '',
                'State: before/after': '',
                'Record Type: order/position': event,
                'Trade ID': order_before.trade_id,
                'Position Qty': '-',
                'Symbol': order_before.symbol,
                'Orders Count': '-',
                'Settled Orders': '-',
                'Pending Qty': f"{order_after.pending_qty}",  # Only show new pending qty
                'Executed Qty': order_before.executed_qty,
                'Settled Qty': order_before.settled_qty,
                'Net Qty': order_before.net_qty,
                'Status': order_after.status,
                'Order Side': order_before.order_side
            })
        else:
            timeline.append({
                'Case ID': '',
                'State: before/after': '',
                'Record Type: order/position': event,
                'Trade ID': orders_before[event].trade_id,
                'Position Qty': '-',
                'Symbol': orders_before[event].symbol,
                'Orders Count': '-',
                'Settled Orders': '-',
                'Pending Qty': orders_before[event].pending_qty,
                'Executed Qty': orders_before[event].executed_qty,
                'Settled Qty': orders_before[event].settled_qty,
                'Net Qty': orders_before[event].net_qty,
                'Status': orders_before[event].status,
                'Order Side': orders_before[event].order_side
            })
    
    # Add AFTER position
    timeline.append({
        'Case ID': next_case_id,
        'State: before/after': 'after',
        'Record Type: order/position': 'POSITION',
        'Trade ID': position_after.trade_id,
        'Position Qty': position_after.poston_qty,
        'Symbol': position_after.symbol,
        'Orders Count': len(position_after.orders['buy']) + len(position_after.orders['sell']),
        'Settled Orders': len(position_after.settled_orders['buy']) + len(position_after.settled_orders['sell']),
        'Pending Qty': '-',
        'Executed Qty': '-',
        'Settled Qty': '-',
        'Net Qty': '-',
        'Status': '-',
        'Order Side': '-'
    })
    
    # Add AFTER orders
    for order_name, order in orders_after.items():
        timeline.append({
            'Case ID': '',
            'State: before/after': '',
            'Record Type: order/position': order_name,
            'Trade ID': order.trade_id,
            'Position Qty': '-',
            'Symbol': order.symbol,
            'Orders Count': '-',
            'Settled Orders': '-',
            'Pending Qty': order.pending_qty,
            'Executed Qty': order.executed_qty,
            'Settled Qty': order.settled_qty,
            'Net Qty': order.net_qty,
            'Status': order.status,
            'Order Side': order.order_side
        })
    
    # Create DataFrame with specific column order
    columns = [
        'Case ID', 'State: before/after', 'Record Type: order/position', 
        'Trade ID', 'Position Qty', 'Symbol', 'Orders Count', 'Settled Orders',
        'Pending Qty', 'Executed Qty', 'Settled Qty', 'Net Qty', 'Status', 'Order Side'
    ]
    # Convert timeline to DataFrame with explicit columns
    df = pd.DataFrame(timeline, columns=columns)
    append_to_excel(df, excel_file)

def append_to_excel(df_new, file_path):
    if os.path.exists(file_path):
        # Read existing data with explicit columns
        df_existing = pd.read_excel(file_path, index_col=None, usecols=df_new.columns)
        
        # Check if this test case already exists
        last_case_id = df_new['Case ID'].iloc[0]
        df_existing = df_existing[df_existing['Case ID'] != last_case_id]
        
        # Combine and write, ensuring no extra columns
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_excel(file_path, index=False, columns=df_new.columns)
    else:
        df_new.to_excel(file_path, index=False, columns=df_new.columns)

def get_next_case_id(file_path):
    if not os.path.exists(file_path):
        return 1
    try:
        df = pd.read_excel(file_path, index_col=None)  # Add index_col=None
        return 1 if df.empty else int(df['Case ID'].max()) + 1
    except:
        return 1

def create_test_order(trade_id, pending_qty, executed_qty, status, order_side, symbol='TCS', order_id=None, price=None):
    """Helper function to create orders easily"""
    return Order(
        trade_id=trade_id,
        pending_qty=pending_qty,
        executed_qty=executed_qty,
        status=status,
        order_side=order_side,
        symbol=symbol,
        order_id=order_id,
        price=price  # <-- Pass price
    )

def run_test():
    orders = {}
    orders_before = {}
    modified_orders = {}
    event_sequence = []

    position = Position(trade_id=111)
    position_before = deepcopy(position)

    # Order 1: Buy, 100 @ 10, then 100 @ 12 (avg 11)
    order1 = Order(trade_id=111, pending_qty=300, executed_qty=0, status='pending', order_side='buy', symbol='TCS', order_id='ORDER-1')

    order1.modify_order_execute_qty(100, 10)
    # order1.modify_order_pending_qty(10, 14)
    # avg1 = 10
    order1.modify_order_execute_qty(100, 12)
    #pending_qty = 10
    # avg1 = 11
    orders['ORDER-1'] = order1
    orders_before['ORDER-1'] = deepcopy(order1)
    position.add_order(order1)
    order1.modify_order_pending_qty(10, 14)
    # avg1 = 11
    event_sequence.append('ORDER-1')

    # Order 2: Sell, 60 @ 9, then 40 @ 19 (avg 13)
    order2 = Order(trade_id=111, pending_qty=100, executed_qty=0, status='pending', order_side='sell', symbol='TCS', order_id='ORDER-2')
    order2.modify_order_execute_qty(40, 9)
    # avg2 = 9
    order2.modify_order_execute_qty(40, 19)
    # avg2 = 14


    orders['ORDER-2'] = order2
    orders_before['ORDER-2'] = deepcopy(order2)

    # order1 - 200qty(pending - 0) - 11rs
    # order2 - 80qty(pending - 20) - 14rs

    position.add_order(order2)
    
    # order1 - 120qty(pending - 0) - 11rs
    # order2 - 0qty(pending - 20) - 14rsxx


    # net_qty = 0 -> order settled => end of life

    # executed_qty = 100
    # net_qty = 80
    # settled_qty = 20

    event_sequence.append('ORDER-2')

    order2.modify_order_execute_qty(20, 10)

    event_sequence.append('ORDER-2')

    position.print_settled_trades()

    print(order1)
    print(order2)
    log_test_case(position_before, position, orders_before, orders, modified_orders, event_sequence)

def main():
    print("Starting Position Manager Test")
    print("=" * 50)
    run_test()
    print("=" * 50)
    print("Test Complete")
    # for trade in position.settled_trades:
    #     print(trade)

if __name__ == "__main__":
    main()