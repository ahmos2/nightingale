from ws4py.websocket import WebSocket
class WSHandler(WebSocket):
    def received_message(self, message):
        print message
        cherrypy.engine.publish('websocket-broadcast',message)