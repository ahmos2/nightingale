import cherrypy,json,hmac,hashlib,statemanager
from argumentHandler import *
class watchdog(object):
    state=statemanager.StateManager()
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
        self.state.set(self.state.UniqueName(company,ship,controller,instance), "lastAlive",(day,ms))
        cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"alive","company":company,"ship":ship,"controller":controller,"instance":instance,"day":day,"ms":ms}))
        return "ok"
    @cherrypy.expose
    def Reset(self,company,ship,controller,instance,signature):
        print company,ship,controller,instance
        self.state.set(self.state.UniqueName(company,ship,controller,instance), "signature", args.signature)
        if self.CheckSignature(company,ship,controller,instance,signature):
            cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"reset","company":company,"ship":ship,"controller":controller,"instance":instance}))
            return "ok"
        cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"error","company":company,"ship":ship,"controller":controller,"instance":instance,"error":"Signature check failed"}))
        return "Signature check failed"
    @cherrypy.expose
    def ResetErrorState(self,company,ship,controller,instance):
        cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"reseterrorstate","company":company,"ship":ship,"controller":controller,"instance":instance}))
        self.state.set(self.state.UniqueName(company,ship,controller,instance), "lastError",None)
        self.state.set(self.state.UniqueName(company,ship,controller,instance), "errorLevel",None)
        self.state.set(self.state.UniqueName(company,ship,controller,instance), "warningLevel",None)
    @cherrypy.expose
    def Alert(self,company,ship,controller,instance,error,signature):
        print company,ship,controller,instance,error
        if not self.CheckSignature(company,ship,controller,instance,signature):
            cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"error","company":company,"ship":ship,"controller":controller,"instance":instance,"error":"Signature check failed"}))
            return "Signature check failed"
        cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"error","company":company,"ship":ship,"controller":controller,"instance":instance,"error":error}))
        self.state.set(self.state.UniqueName(company,ship,controller,instance), "lastError",(error,self.state.get(self.state.UniqueName(company,ship,controller,instance), "lastAlive")))
        if self.state.get(self.state.UniqueName(company,ship,controller,instance), "errorLevel") <> None:
            self.state.set(self.state.UniqueName(company,ship,controller,instance), "errorLevel",self.state.get(self.state.UniqueName(company,ship,controller,instance), "errorLevel")+1)
        else:
            self.state.set(self.state.UniqueName(company,ship,controller,instance), "errorLevel",1)
        return "ok"
    @cherrypy.expose
    def State(self):
        return "Not implemented"
    @cherrypy.expose
    def ws(self):
        cherrypy.request.ws_handler
    def CheckSignature(self,company,ship,controller,instance,signature):
        self.prevSignature = self.state.get(self.state.UniqueName(company,ship,controller,instance), "signature")

        self.state.set(self.state.UniqueName(company,ship,controller,instance), "company", company)
        self.state.set(self.state.UniqueName(company,ship,controller,instance), "ship", ship)
        self.state.set(self.state.UniqueName(company,ship,controller,instance), "controller", controller)
        self.state.set(self.state.UniqueName(company,ship,controller,instance), "instance", instance)

        if self.prevSignature <> None:
            sign2be = hmac.new(self.privatekey, self.prevSignature, hashlib.sha512).hexdigest()
            print sign2be[:8],signature[:8],self.prevSignature[:8]
        if self.prevSignature == None or sign2be == signature:
            self.state.set(self.state.UniqueName(company,ship,controller,instance), "signature", signature)
            return True
        self.state.set(self.UniqueName(company,ship,controller,instance), "signatureCheckFail", (signature,self.state.get(self.UniqueName(company,ship,controller,instance), "lastAlive")))
        return False
