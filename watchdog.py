import cherrypy,json,hmac,hashlib
from argumentHandler import *
class watchdog(object):
    instanceState={}
    privatekey=args.privatekey

    @cherrypy.expose
    def index(self):
        return "Hello world!"
    @cherrypy.expose
    def Alive(self,company,ship,controller,instance,day,ms,signature):
        print company,ship,controller,instance,day,ms
        if not self.CheckSignature(company,ship,controller,instance,signature):
            cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"error","company":company,"ship":ship,"controller":controller,"instance":instance,"error":"Signature check failed"}))
            return "Signature check failed"
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "lastAlive",(day,ms))
        cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"alive","company":company,"ship":ship,"controller":controller,"instance":instance,"day":day,"ms":ms}))
        return "ok"
    @cherrypy.expose
    def Reset(self,company,ship,controller,instance,signature):
        print company,ship,controller,instance
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "signature", args.signature)
        if self.CheckSignature(company,ship,controller,instance,signature):
            return "ok"
        return "Signature check failed"
    @cherrypy.expose
    def ResetErrorState(self,company,ship,controller,instance):
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "lastError",None)
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "errorLevel",None)
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "warningLevel",None)
    @cherrypy.expose
    def Alert(self,company,ship,controller,instance,error,signature):
        print company,ship,controller,instance,error
        if not self.CheckSignature(company,ship,controller,instance,signature):
            cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"error","company":company,"ship":ship,"controller":controller,"instance":instance,"error":"Signature check failed"}))
            return "Signature check failed"
        cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"error","company":company,"ship":ship,"controller":controller,"instance":instance,"error":error}))
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "lastError",(error,self.getStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "lastAlive")))
        if self.getStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "errorLevel") <> None:
            self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "errorLevel",self.getStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "errorLevel")+1)
        else:
            self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "errorLevel",1)
        return "ok"
    @cherrypy.expose
    def State(self):
        return json.dumps(self.instanceState)
    @cherrypy.expose
    def ws(self):
        cherrypy.request.ws_handler
    def CheckSignature(self,company,ship,controller,instance,signature):
        self.prevSignature = self.getStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "signature")

        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "company", company)
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "ship", ship)
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "controller", controller)
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "instance", instance)

        if self.prevSignature <> None:
            sign2be = hmac.new(self.privatekey, self.prevSignature, hashlib.sha512).hexdigest()
            print sign2be[:8],signature[:8],self.prevSignature[:8]
        if self.prevSignature == None or sign2be == signature:
            self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "signature", signature)
            return True
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "signatureCheckFail", (signature,self.getStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "lastAlive")))
        return False
    def UniqueNameForInstance(self,company,ship,controller,instance):
        return company+":"+ship+":"+controller+":"+instance
    def getStateValue(self,instanceName, key):
        if not self.instanceState.has_key(instanceName):
            return None
        if not self.instanceState[instanceName].has_key(key):
            return None
        return self.instanceState[instanceName][key]
    def setStateValue(self,instanceName, key, value):
        if not self.instanceState.has_key(instanceName):
            self.instanceState[instanceName]={}
        self.instanceState[instanceName][key]=value
