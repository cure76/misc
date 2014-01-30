# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json
import uuid

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

import schematics
from schematics import models
from schematics.types import ( UUIDType, IntType, StringType, BaseType )
from schematics.types.compound import ( ListType, DictType, ModelType )

#class ValidateError(schematics.exceptions.ModelValidationError):
#    pass
    
ValidateError = schematics.exceptions.ModelValidationError

class ErrResponse(models.Model):
    code = IntType(required=False, serialize_when_none=False)
    message = StringType(required=False, serialize_when_none=False)

class ResponseModel(models.Model):
    ''' JSON-RPC response model '''
    jsonrpc = StringType(required=True, default='2.0')
    id = StringType(required=False)
    result = BaseType(required=False, serialize_when_none=False)
    error = ModelType(ErrResponse, default=ErrResponse(), required=False, serialize_when_none=False)

class RequestModel(models.Model):
    ''' JSON-RPC request model '''
    jsonrpc = StringType(required=True, default='2.0')
    id = StringType(required=False)
    method = StringType(required=True)
    params = BaseType(required=False)

class Response(ResponseModel):
    ''' JSON-RPC Response '''
    
    def __str__(self):
        return '%s: %s' % (Response.__name__, self.to_json())
        
    def to_json(self):
        return json.dumps(self.to_primitive())
    
    @classmethod
    def from_json(cls, jsonstring):
        ''' parse response jsonstring '''
        
        data = {}
        
        def parser(jsonstring):
            try:
                data = json.loads(jsonstring)
                
            except ValueError:
                raise JsonRpcParseError()
                
            finally:
                return data

        data = parser(jsonstring)
        Resp = cls(data)
        return Resp

class Request(RequestModel):
    ''' JSON-RPC request model '''
        
    @classmethod
    def from_json(cls, jsonstring):
        ''' parse request jsonstring '''
        
        data = {}
        
        def parser(jsonstring):
            try:
                data = json.loads(jsonstring)
            except ValueError:
                raise JsonRpcParseError()
            else:
                return data
        try:
            data = parser(jsonstring)
            
            if not 'method' in data or not data['method']:
                raise JsonRpcInvalidRequestError()

            if 'params' in data:
                if isinstance(data['params'], dict):
                    class Request(cls):
                        params = DictType(BaseType)
                    Req = Request(data)
                    
                elif isinstance(data['params'], list or tuple):
                    class Request(cls):
                        params = ListType(BaseType)
                    Req = Request(data)
                    
                else:
                    raise JsonRpcInvalidParamsError()
            else:
                Req = cls(data)

        except (
                JsonRpcParseError, 
                JsonRpcInvalidParamsError, 
                JsonRpcInvalidRequestError
        ), ex:
            Req = cls(data)
            Req.Response.error = {'code': ex.code, 'message': ex.message}
            Req.Response.id = data.get('id')
            return Req

        finally:
            return Req

    def __str__(self):
        return '%s: %s' % (Request.__name__, self.to_json())

    def __repr__(self):
        return self.to_json()

    def to_json(self):
        return json.dumps(self.to_primitive())

    def is_valid(self):
        if self.Response.error.to_native():
            return False
        return True
        
    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        
        # set id
        not self.id and setattr(self, 'id', uuid.uuid4().__str__())
        
        # set Response
        self.Response = Response()
        self.Response.id = self.id


if __name__ == '__main__':
    ''' '''
    
    reqstring = {
        'jsonrpc':'2.0', 
        'id': '73555b67-a3ca-4987-b944-4d5458863500', 
        'method': 'Resource::Add', 
        'params': {'hostname':'sex.ua'}
    }
    
    jsonstring = json.dumps(reqstring)
    
    jsonstring = '>>>'
    
    Req = Request.from_json(jsonstring)
    print Req.method
    print Req.is_valid()
    
    print Req.Response
    
    
    
#    Req = Request()
#    Req.method = 'Resource::Add'
#    
#    
#    print Req.to_native()
#    print Req.to_primitive()
#    print dir(Req)
#    
#    print Req
    
    
    
    
