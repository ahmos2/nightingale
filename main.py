import cherrypy,os,json,hmac,hashlib,ptvsd,argparse
ptvsd.enable_attach(secret = 'joshua')
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket,EchoWebSocket
from cherrypy.lib import auth_basic

cherrypy.config.update({'server.socket_host' : '0.0.0.0'})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

USER={'ws2log':'ws2log', 'admin':'admin'}

class WSHandler(WebSocket):
    def received_message(self, message):
        print message
        cherrypy.engine.publish('websocket-broadcast',message)

class watchdog(object):
    instanceState={}

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
        prevSignature = self.getStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "signature")

        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "company", company)
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "ship", ship)
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "controller", controller)
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "instance", instance)

        if prevSignature <> None:
            sign2be = hmac.new(privatekey, prevSignature, hashlib.sha512).hexdigest()
            print sign2be[:8],signature[:8],prevSignature[:8]
        if prevSignature == None or sign2be == signature:
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

parser=argparse.ArgumentParser()
parser.add_argument("--privatekey", help="Key to verify signatures", default="Never gonna give you up")
parser.add_argument("--signature", help="Initial signature", default="Never gonna let you down")
parser.add_argument("--certkey", help="Private key for the server certificate", default="/home/pi/certificate/remote1.key")
parser.add_argument("--certificate",help="Server certificate", default="/home/pi/certificate/remote1.crt")
parser.add_argument("--certchain",  help="Certs for root and intermediate CAs", default="/home/pi/certificate/rootCA.pem")
args=parser.parse_args()

privatekey=args.privatekey
cherrypy.config.update(
                       {
                           'server.ssl_module':'builtin',
                           'server.ssl_certificate':args.certificate,
                           'server.ssl_private_key':args.certkey,
                           'server.certificate_chain':args.certchain,
                           '/static' : 
                               {
                                   'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
                               }
                       }
)
                       


print cherrypy.config
cherrypy.quickstart(watchdog(),"/",config={
    '/ws': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': WSHandler,
        'tools.auth_basic.on': True,
        'tools.auth_basic.realm': 'nightingale',
        'tools.auth_basic.checkpassword': auth_basic.checkpassword_dict(USER),
    },
    '/static' : {
        'tools.staticdir.on'            : True,
        'tools.staticdir.dir'           : os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static'),
        'tools.auth_basic.on': True,
        'tools.auth_basic.realm': 'nightingale',
        'tools.auth_basic.checkpassword': auth_basic.checkpassword_dict(USER)
  }
})
