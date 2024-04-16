from pymongo.mongo_client import MongoClient

from backend.subscriptions_service.DAO.Implementation.BenefitDAO      import BenefitDAO
from backend.subscriptions_service.DAO.Implementation.SubscriptionDAO import SubscriptionDAO

from backend.subscriptions_service.Entities.JSONFactory.Implementation.BenefitJSONFactory import BenefitJSONFactory
from backend.subscriptions_service.Entities.JSONFactory.Implementation.SubPlanJSONFactory import SubPlanJSONFactory

from backend.subscriptions_service.Entities.Benefit          import Benefit
from backend.subscriptions_service.Entities.SubscriptionPlan import SubscriptionPlan


from flask import Flask , request, json 


class SubscriptionController(object):
    """
    Class to control Subscription HTTP requests

    Arguments
    -------
    mongo_client : The mongo client of the database 
    
    """
    def __init__(self,
                 mongo_client : MongoClient): 
        
        self.__benefitdao = BenefitDAO(mongo_client = mongo_client)
        self.__subdao     = SubscriptionDAO(mongo_client = mongo_client)
        
        self.__benefitfactory = BenefitJSONFactory()
        self.__subscriptionfactory = SubPlanJSONFactory()
        
        self.__app = Flask(
            import_name = __name__
        )
        
        self.__app.add_url_rule(
            rule = '/add',
            view_func = self.__add_subscription,
        )
        
        self.__app.add_url_rule(
            rule = '/delete',
            view_func = self.__remove_subscription,
        )
        
        self.__app.add_url_rule(
            rule = '/find_subscription',
            view_func = self.__find_subscription,
        )
        
        self.__app.add_url_rule(
            rule = '/find_subscription_details',
            view_func = self.__find_subscription_benefits,
        )
        
        self.__app.add_url_rule(
            rule = '/check_expiry',
            view_func = self.__check_if_subscription_expired,
        )
    
    def runApp(self, port : int):
        self.__app.run(debug = True)
    
    # 405 
    def generateIncorrectRequest(self):
        res = {
            'message' : 'Request not allowed, use GET only' 
        }
        return self.__app.response_class(
            response = json.dumps(res),
            status = 405, 
            mimetype = 'application/json',
        )
    
    # 400
    def badRequest(self, e):
        print(e) 
        res = {
            'message' : 'Bad Request',
        }
        
        return self.__app.response_class(
            response = json.dumps(res),
            status = 400, 
            mimetype = 'application/json',
        )
    
    # 200 
    def sendResponse(self, response):
        return self.__app.response_class(
            response = json.dumps(response),
            status = 200, 
            mimetype = 'application/json',
        )
         
    
    def __add_subscription(self): 
        if request.method == 'GET':
            try:
                body = request.form 
                
                benefit = self.__benefitfactory.convertToObject(body)
                benefit_id = self.__benefitdao.add(benefit = benefit)

                
                body = dict(body) 
                body['benefit_id'] = str(benefit_id)
                subscription = self.__subscriptionfactory.convertToObject(body) 
                subscription_id = self.__subdao.add(subscription)
            
                return self.sendResponse({
                    'message' : 'OK',
                    'subscription_id' : str(subscription_id),
                })
            
            except Exception as e:
                return self.badRequest(e) 
        else:
            return self.generateIncorrectRequest()
    
    
    def __remove_subscription(self):
        if request.method == 'GET':
            try: 
              userid = request.form.get("userid") 
              benefit_id = self.__subdao.remove(userid = userid)  
              self.__benefitdao.remove(mongo_id = benefit_id)
              
              return self.sendResponse({
                  'message' : 'OK',
                  'deleted' : 'yes',
              })
            except Exception as e: 
                return self.badRequest(e) 
        else: 
            return self.generateIncorrectRequest()
     
     
    def __find_subscription(self):
        if request.method == 'GET':
            try: 
                userid = request.form.get("userid") 
                
                subscription = self.__subdao.find(userid = userid)
                
                if subscription == None: 
                    return self.sendResponse({
                        'message' : 'Not Found',
                    })
                
                json_sub = self.__subscriptionfactory.convertToJSON(subscription) 
                
                return self.sendResponse({
                    'message' : 'OK',
                    'subscription_details' : json_sub,
                })
                
            except Exception as e: 
                return self.badRequest(e) 
            
        else:
            return self.generateIncorrectRequest()
    
    def __find_subscription_benefits(self):
        if request.method == 'GET':
            try: 
                userid = request.form.get("userid") 
                subscription = self.__subdao.find(userid = userid)
                
                if subscription == None: 
                    return self.sendResponse({
                        'message' : 'Not Found',
                    })
                if subscription.checkExpired() == True: 
                    return self.sendResponse({
                        'message' : 'expired',
                    })
                    
                benefit_id = subscription.getBenefit() 
                
                benefit = self.__benefitdao.find(mongo_id = benefit_id)  
                
                
                json_benefit = self.__benefitfactory.convertToJSON(benefit) 
                
                return self.sendResponse({
                    'message' : 'OK',
                    'benefit_details' : json_benefit,
                })
                
            except Exception as e: 
                return self.badRequest(e) 
            
        else:
            return self.generateIncorrectRequest()
    
    def __check_if_subscription_expired(self):
        if request.method == 'GET':
            try: 
                userid = request.form.get("userid") 
                subscription = self.__subdao.find(userid = userid)
                
                if subscription == None: 
                    return self.sendResponse({
                        'message' : 'Not Found',
                    })
                isExpired = subscription.checkExpired() 
                
                return self.sendResponse({
                    'message' : 'OK',
                    'isExpired' : isExpired,
                })
            except Exception as e: 
                return self.badRequest(e) 
        else: 
           return self.generateIncorrectRequest()