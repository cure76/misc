# -*- coding: utf-8 -*-

import uuid
#import bson

import json
from datetime import datetime
import decimal

class JsonRpcServerError(Exception):
    # -32099 to -32000 free for application-defined codes
    code = -32000
    message = 'Server error'
    def __init__(self, message=None):
        message and setattr(self, "message", message)
        super(JsonRpcServerError, self).__init__(self.message)

class JsonRpcInternalError(JsonRpcServerError):
    code = -32603
    message = 'Internal error'

class JsonRpcInvalidParamsError(JsonRpcServerError):
    code = -32602
    message = 'Invalid params'

class JsonRpcMethodNotFoundError(JsonRpcServerError):
    code = -32601
    message = 'Method not found'

class JsonRpcInvalidRequestError(JsonRpcServerError):
    code = -32600
    message = 'Invalid Request'
    
class JsonRpcTooBigError(JsonRpcInvalidRequestError):
    message = 'Message too big'

class JsonRpcParseError(JsonRpcServerError):
    code = -32700
    message = 'Parse error'
    
class JsonRpcClientError(JsonRpcServerError):
    code = -32000
    message = 'Server error'

class JsonRpcEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
            
        elif isinstance(obj, uuid.UUID):
            return obj.__str__()
            
        elif hasattr(obj, "wrap"):
            return obj.wrap()
            
#        elif isinstance(obj, bson.ObjectId):
#            return obj.__str__()
            
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
            
#        elif isinstance(obj, IPAddress): # or isinstance(obj, PhoneNumber) or isinstance(obj, EncryptedString):
#            return str(obj)

        raise TypeError("%r is not JSON serializable" % (obj,))

def dump_request(method, params, req_id=None, encoder=JsonRpcEncoder, indent=None):
    """ """
    req_id = req_id or uuid.uuid4().__str__()
    obj = {"jsonrpc": "2.0", "method": method, "params": params, "id": req_id}
    return json.dumps(obj, cls=encoder, indent=indent)

def dump_response(result, req_id=None, encoder=JsonRpcEncoder, indent=None):
    """ """
    obj = {"jsonrpc": "2.0", "result": result, "id": req_id}
    return json.dumps(obj, cls=encoder, indent=indent)

def dump_error(error, req_id=None, encoder=JsonRpcEncoder):
    _err = {'code': None, 'message':None}
    if isinstance(error, dict):
        error.has_key('code') and _err.update({'code': error['code']})
        error.has_key('message') and _err.update({'message': error['message']})
    obj = {"jsonrpc": "2.0", "error": _err, "id": req_id}
    return json.dumps(obj, cls=encoder)

def load_string(string):
#    return json.loads(string, parse_float=decimal.Decimal)
    return json.loads(string)

class Request(object):
    """ 
    
    """
    keys = ('jsonrpc', 'id', 'method', 'params')
    
    def __init__(self, method=None, params=None, id=None, jsonrpc=None):
        """ """
        # set default
        map(lambda key: setattr(self, key, None), self.keys)
        # set by arguments
        method and setattr(self, 'method', method)
        params and setattr(self, 'params', params)
        setattr(self, 'id', id or uuid.uuid4().__str__()) 
        setattr(self, 'jsonrpc', jsonrpc or '2.0') 

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.__dict__)

    def json(self, indent=None):
        return dump_request(self.method, self.params, req_id=self.id, indent=indent)

#    def sha256(self):
#        return sha256('%s:%s' % (str(self.method), str(sorted(self.params))))

    @classmethod
    def unwrap(cls, req):
        try:
            req_data = load_string(req)
            Req = Request(**req_data)
            return Req
        except ValueError:
            raise JsonRpcParseError()

class Response(object):
    ''' jsonrpc response object '''
    
    def __init__(self, result=None, id=None, error=None, jsonrpc='2.0'):
        ''' '''
        self.result = result
        self.id = id
        self.error = error
        self.jsonrpc = jsonrpc
    
    def __eq__(self, req_id):
        return str(self.id) == str(req_id)
    
    def json(self):
        ''' response to json '''
        if not self.error:
            return dump_response(self.result, req_id=self.id)
        else:
            return dump_error(self.error, req_id=self.id)

    @classmethod
    def unwrap(cls, res):
        ''' unwrap json string '''
        try:
            res_data = load_string(res)
            Res = cls(**res_data)
            return Res
        except ValueError:
            raise JsonRpcParseError()

if __name__ == "__main__":
    """ """
    

