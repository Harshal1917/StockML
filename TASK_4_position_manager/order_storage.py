#http://localhost:5984/_utils/


#DONE#TODO: couchdb install

#TODO: save and load orders
#TODO: create positions from orders

import couchdb

class Trades:

    orders_db = "orders"
    # accounts_db = "accounts"

    def __init__(self):
        self.__server = couchdb.Server('http://admin:admin@localhost:5984/')
        # Create orders database if it doesn't exist
        if Trades.orders_db not in self.__server:
            self.__server.create(Trades.orders_db)
        # self.__accounts_db = self.__server[Trades.accounts_db]
        self.__orders_db = self.__server[Trades.orders_db]
        design_doc = {
            "_id": "_design/OrderInfo",
            "views": {
                "BrokerId": {
                    "map": "function(doc) { emit([doc.broker_order_id, doc.account_id], doc); }"
                },
                "StrategyOrders": {
                    "map": "function(doc) { emit([doc.strategy_id, doc.account_id, doc.status], doc); }"
                },
                "ActiveOrders": {
                    "map": "function(doc) { if (doc.Status === 'open' || doc.status === 'pending' || doc.status === 'partial_executed') { emit([doc.strategy_id, doc.account_id], doc); } }"
                }
            },
            "language": "javascript"
        }        
        try:
            if "_design/OrderInfo" in self.__orders_db:
                doc = self.__orders_db["_design/OrderInfo"]
                doc.update(design_doc)
                self.__orders_db.save(doc)
            else:
                self.__orders_db.save(design_doc)
            print("success: True, Views created/updated successfully")
        except:
            print("error")        


    def AddOrder(self, order_id, doc):
        
        try:
    
            doc['_id'] = order_id

            if order_id in self.__orders_db:
                return {"error": "Order ID already exists"}
        
            self.__orders_db.save(doc)
            return {"success": True, "order_id": order_id, "message": "Order added successfully"}
        
        except couchdb.http.ResourceConflict:
            return {"error": "Resource conflict, the document may already exist"}
        
        except Exception as e:
            return {"error": str(e)}
        
    def ModifyOrder(self, order_id, update_doc):
        
        try:

            if order_id in self.__orders_db:
                existing_doc = self.__orders_db[order_id]

                for key, value in update_doc.items():
                    existing_doc[key] = value

                self.__orders_db.save(existing_doc)
                return {"success": True, "order_id": order_id, "message": "Order modified successfully"}    

            else:
                return {"error": "Order not found", "order_id": order_id}
            
        except couchdb.http.ResourceConflict:
            return {"error": "Resource conflict, the document may have been modified by another process"}
        
        except Exception as e:
            return {"error": str(e)}    


    def DeleteOrder(self, order_id):
        try:
        
            if order_id in self.__orders_db:
                
                doc = self.__orders_db[order_id]
               
                self.__orders_db.delete(doc)

                return {"success": True, "order_id": order_id, "message": "Order deleted successfully"}
            else:
                return {"error": "Order not found", "order_id": order_id}
        
        except Exception as e:
            return {"error": str(e)}
        

    def ModifyOrderByBrokerId(self, broker_order_id, account_id, updated_data):
   
        try:
            
            result = self.__orders_db.view(
                "OrderInfo/BrokerId", 
                key=[broker_order_id, account_id]
            )

            if len(result) == 0:
                return {"error": "Order not found", "broker_order_id": broker_order_id, "account_id": account_id}

            doc_id = result.rows[0].id
            order_doc = self.__orders_db[doc_id]

            for key, value in updated_data.items():
                order_doc[key] = value

            self.__orders_db.save(order_doc)
            return {"success": True, "broker_order_id": broker_order_id, "message": "Order modified successfully"}

        except couchdb.http.ResourceConflict:
            return {"error": "Resource conflict"}
        except Exception as e:
            return {"error": str(e)}


    def GetOrder(self, broker_order_id, account_id):

        try:
            
            result = self.__orders_db.view(
                "OrderInfo/BrokerId",
                key=[broker_order_id, account_id]
            )

            if len(result) == 0:
                return {"error": "Order not found", "broker_order_id": broker_order_id, "account_id": account_id }

            order_doc = result.rows[0].value
            return {"success": True, "order": order_doc}

        except Exception as e:
            return {"error": str(e)}


    def GetOrdersForStrategy(self, strategy_id, account_id, status):

        try:
        
            result = self.__orders_db.view(
                "OrderInfo/StrategyOrders",
                key=[strategy_id, account_id, status]
            )

            orders = [row.value for row in result]
            if not orders:
                return { 
                    "error": "No orders found",
                    "strategy_id": strategy_id,
                    "account_id": account_id,
                    "status": status
                }

            return {
                "success": True,
                "orders": orders,
                "message": f"{len(orders)} order(s) found."
            }

        except Exception as e:
            return {"error": str(e)}


    def GetActiveOrdersForStrategy(self, strategy_id, account_id):

        try:
         
            result = self.__orders_db.view(
                "OrderInfo/ActiveOrders",
                key=[strategy_id, account_id]
            )

            active_orders = [row.value for row in result]
            if not active_orders:
                return {
                    "error": "No active orders found",
                    "strategy_id": strategy_id,
                    "account_id": account_id
                }

            return {
                "success": True,
                "orders": active_orders,
                "message": f"{len(active_orders)} active order(s) found."
            }

        except Exception as e:
            return {"error": str(e)}
