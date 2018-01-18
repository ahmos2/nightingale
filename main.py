import os #,ptvsd
#ptvsd.enable_attach(secret = 'joshua')
from argumentHandler import *
from watchdog import *
from WSHandler import *
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from cherrypy.lib import auth_basic

cherrypy.config.update({'server.socket_host' : '0.0.0.0'})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

USER={'ws2log':'ws2log', 'admin':'admin', 'remote':'remote'}

privatekey=args.privatekey
cherrypy.config.update(
                       {
                           'server.ssl_module':'builtin',
                           'server.ssl_certificate':args.certificate,
                           'server.ssl_private_key':args.certkey,
                           'server.certificate_chain':args.certchain,
                           'tools.auth_basic.on': True,
                           'tools.auth_basic.realm': 'nightingale',
                           'tools.auth_basic.checkpassword': auth_basic.checkpassword_dict(USER),
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
