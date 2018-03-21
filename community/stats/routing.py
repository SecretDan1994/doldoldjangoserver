from channels.routing import route
from . import consumers

gs_inner_routing = [
	route("websocket.connect", consumers.gs_connect, path=r"^/(?P<secretkey>[-\w]+)/$"),
#	route("websocket.connect", consumers.gs_connect, path=r"^/(?P<secretkey>[-\w]+)/$"),
	route("websocket.receive", consumers.gs_receive),
	route("websocket.disconnect", consumers.gs_disconnect),
]

ws_inner_routing = [
	#route("websocket.connect", consumers.ws_connect),
	route("websocket.connect", consumers.ws_connect, path=r'^/servers/(?P<GameServer_id>[0-9]+)/stats/$'),
	route("websocket.receive", consumers.ws_receive),
	route("websocket.disconnect", consumers.ws_disconnect),
]
