from position import Position, Order
from callbacks import register_all_callbacks
import pandas as pd
from copy import deepcopy
import os

def create_test_case_data(case_id, position_before, position_after, orders_before, orders_after, modified_order=None, modified_order_num=None):
    """Create a list of dictionaries representing the test case data."""
    data = []
    
    # Add BEFORE position
    data.append({
        'Case ID': case_id,
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
    
    # Add BEFORE orders
    for i, order in enumerate(orders_before, 1):
        data.append({
            'Case ID': '',
            'State: before/after': '',
            'Record Type: order/position': f'ORDER-{i}',
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
    
    # Add modification order to BEFORE state
    if modified_order and modified_order_num:
        data.append({
            'Case ID': '',
            'State: before/after': '',
            'Record Type: order/position': f'ORDER-{modified_order_num}_modification',
            'Trade ID': modified_order.trade_id,
            'Position Qty': '-',
            'Symbol': modified_order.symbol,
            'Orders Count': '-',
            'Settled Orders': '-',
            'Pending Qty': modified_order.pending_qty,
            'Executed Qty': modified_order.executed_qty,
            'Settled Qty': modified_order.settled_qty,
            'Net Qty': modified_order.executed_qty,  # Initial net qty before settlement
            'Status': modified_order.status,
            'Order Side': modified_order.order_side
        })
    
    # Add AFTER position
    data.append({
        'Case ID': case_id,
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
    for i, order in enumerate(orders_after, 1):
        data.append({
            'Case ID': '',
            'State: before/after': '',
            'Record Type: order/position': f'ORDER-{i}',
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
    
    return data

def get_next_case_id(file_path):
    """Get the next case ID from existing Excel file"""
    if not os.path.exists(file_path):
        return 1
    
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            return 1
        return int(df['Case ID'].max()) + 1
    except:
        return 1

def append_to_excel(df_new, file_path):
    """Append new data to existing Excel file or create new one"""
    if os.path.exists(file_path):
        # Read existing data
        df_existing = pd.read_excel(file_path)
        # Concatenate with new data
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        # Write back to file
        df_combined.to_excel(file_path, index=False)
    else:
        # Create new file if it doesn't exist
        df_new.to_excel(file_path, index=False)

def main():
    excel_file = 'position_order_test_cases.xlsx'
    
    # Create a Position instance
    position = Position(trade_id=111)
    
    # Register all callbacks
    register_all_callbacks(position)

    # Create Order instances
    order0 = Order(trade_id=111, pending_qty=0, executed_qty=1500, 
                status='executed', order_side='buy', symbol='TCS')
    order1 = Order(trade_id=111, pending_qty=100, executed_qty=100, 
                  status='partially_executed', order_side='buy', symbol='TCS')
    order2 = Order(trade_id=111, pending_qty=0, executed_qty=200, 
                  status='executed', order_side='sell', symbol='TCS')
    order3 = Order(trade_id=111, pending_qty=500, executed_qty=0,
                  status='pending', order_side='sell', symbol='TCS')
    order4 = Order(trade_id=111, pending_qty=200, executed_qty=100, 
                  status='partially_executed', order_side='sell', symbol='TCS')
    

    
    
    # Store before state with deep copies
    position_before = deepcopy(position)
    orders_before = [
        deepcopy(order0),
        deepcopy(order1),
        deepcopy(order2),
        deepcopy(order3),
        deepcopy(order4)
    ]
    
    print("**********************************before**********************************")
    print(position)
    for order in orders_before:
        print(order)
    print("**********************************before**********************************") 
    
    # Create modification order before adding to position
    modified_order = Order(
        trade_id=111,
        pending_qty=300,  # 500 - 200
        executed_qty=200,
        status='partially_executed',
        order_side='sell',
        symbol='TCS'
    )
    
    # Add orders and perform modification
    position.add_order(order0)
    position.add_order(order1)
    position.add_order(order2)
    position.add_order(order3)
    position.add_order(order4)
    
    # Modify order3 (ORDER-4)
    order3.modify_order_execute_qty(200)
    
    print("\nAfter modification and automatic counter-order matching:")
    print(position)
    
    # Store after state
    position_after = position
    orders_after = [order0, order1, order2, order3, order4]
    
    print("**********************************after**********************************")
    print(position)
    for order in orders_after:
        print(order)
    print("**********************************after**********************************")
    
    # Get next case ID
    next_case_id = get_next_case_id(excel_file)
    
    # Create test case data
    test_case_data = create_test_case_data(
        next_case_id,
        position_before,
        position_after,
        orders_before,
        orders_after,
        modified_order=modified_order,
        modified_order_num=4
    )
    
    # Create DataFrame with new data
    df_new = pd.DataFrame(test_case_data)
    
    # Define the column order to match your desired format
    columns = [
        'Case ID', 'State: before/after', 'Record Type: order/position', 'Trade ID',
        'Position Qty', 'Symbol', 'Orders Count', 'Settled Orders', 'Pending Qty',
        'Executed Qty', 'Settled Qty', 'Net Qty', 'Status', 'Order Side'
    ]
    
    # Reorder columns
    df_new = df_new[columns]
    
    # Append to Excel file
    append_to_excel(df_new, excel_file)
    print(f"\nTest case {next_case_id} has been appended to '{excel_file}'")

if __name__ == "__main__":
    main()