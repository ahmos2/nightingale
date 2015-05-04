import cherrypy,os,json,hmac,hashlib,ptvsd
ptvsd.enable_attach(secret = 'joshua')
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket,EchoWebSocket

cherrypy.config.update({'server.socket_host' : '0.0.0.0'})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

class WSHandler(WebSocket):
    def received_message(self, message):
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
        self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "signature", "Never gonna let you down")
        if self.CheckSignature(company,ship,controller,instance,signature):
            return "ok"
        return "Signature check failed"
    @cherrypy.expose
    def Alert(self,company,ship,controller,instance,error,signature):
        print company,ship,controller,instance,error
        if not self.CheckSignature(company,ship,controller,instance,signature):
            cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"error","company":company,"ship":ship,"controller":controller,"instance":instance,"error":"Signature check failed"}))
            return "Signature check failed"
        cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"error","company":company,"ship":ship,"controller":controller,"instance":instance,"error":error}))
        return "ok"
    @cherrypy.expose
    def ws(self):
        cherrypy.request.ws_handler

    def CheckSignature(self,company,ship,controller,instance,signature):
        prevSignature = self.getStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "signature")
        if prevSignature <> None:
            sign2be = hmac.new(privatekey, prevSignature, hashlib.sha512).hexdigest()
            print sign2be[:8],signature[:8],prevSignature[:8]
        if prevSignature == None or sign2be == signature:
            self.setStateValue(self.UniqueNameForInstance(company,ship,controller,instance), "signature", signature)
            return True
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


privatekey="Never gonna give you up"
cherrypy.config.update(
                       {
                           'server.ssl_module':'builtin',
                           'server.ssl_certificate':'/home/pi/certificate/remote1.crt',
                           'server.ssl_private_key':'/home/pi/certificate/remote1.key',
                           'server.certificate_chain':'/home/pi/certificate/rootCA.pem',
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
            'tools.websocket.handler_cls': WSHandler
            },
  '/static' : {
    'tools.staticdir.on'            : True,
    'tools.staticdir.dir'           : os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
  }
})
