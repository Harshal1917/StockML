from order_storage import Trades

T = Trades()


# ADD ORDER
'''
order_id = 'order11'
doc = {
    "broker_order_id": "B12355",
    "strategy_id": "S011",
    "account_id": "A133",
    "user_id": "U011", 

    "trade_id": "T011",
    "order_end": "entry",
    "Instrument": "AAPL",
    "Order_type": "CNC",
    "Transaction_type": "buy",
    "Quantity": 30,
    "Executed_qty": 0,
    "Executed_avg_price": 0,
    "Limit_price": 450,
    "Trigger_price": 445,
    "Trigger_limit_price": 450,
    "status": "pending"
 }

a = T.AddOrder(order_id, doc)
print(a)
'''




'''
# MODIFY ORDER

order_id = 'order51'
update_doc = {
    "Quantity": 23,
    "Trigger_price": 444,
    "status": "open"
}

b = T.ModifyOrder(order_id, update_doc)
print(b)


'''
"""# DELETE ORDER

order_id = 'order11'
c = T.DeleteOrder(order_id)
print(c)"""





'''
# MODIFY ORDER BY BROKER ID

broker_order_id = "B12355"
account_id = "A133"

updated_data = {
    "Quantity": 60,
    "Executed_qty": 45,
    "status": "partial_executed",
}

d = T.ModifyOrderByBrokerId(broker_order_id, account_id, updated_data)
print(d)




'''


# GET ORDER

broker_order_id = "B12355"
account_id = "A133"

e = T.GetOrder(broker_order_id, account_id)
print(e)



'''

# GET ORDER FOR STRATEGY

strategy_id = "S011"
account_id = "A133"
status = "open"
f = T.GetOrdersForStrategy(strategy_id, account_id, status)
print(f)




'''

'''
# GET ACTIVE ORDER FOR STRATEGY

strategy_id = "S011"
account_id = "A133"
g = T.GetActiveOrdersForStrategy(strategy_id, account_id)
print(g)
'''