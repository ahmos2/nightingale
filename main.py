import cherrypy,os,json
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket,EchoWebSocket

cherrypy.config.update({'server.socket_host' : '0.0.0.0'})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

class WSHandler(WebSocket):
    def received_message(self, message):
        self.send(message.data, message.is_binary)

class watchdog(object):
    @cherrypy.expose
    def index(self):
        return "Hello world!"
    @cherrypy.expose
    def Alive(self,company,ship,controller,instance,day,ms):
        print company,ship,controller,instance,day,ms
        cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"alive","company":company,"ship":ship,"controller":controller,"instance":instance,"day":day,"ms":ms}))
        return "ok"
    @cherrypy.expose
    def Alert(self,company,ship,controller,instance,error):
        print company,ship,controller,instance,error
        cherrypy.engine.publish('websocket-broadcast',json.dumps({"type":"error","company":company,"ship":ship,"controller":controller,"instance":instance,"error":error}))
        return "ok"
    @cherrypy.expose
    def ws(self):
        cherrypy.request.ws_handler


cherrypy.config.update(
                       {
                           '/static' : 
                               {
                                   'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
                               }
                       }
)
                       


print cherrypy.tools.websocket
cherrypy.quickstart(watchdog(),"/",config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': WSHandler
            }
        })
