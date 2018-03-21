from channels.routing import route, include
from stats.routing import gs_inner_routing, ws_inner_routing

channel_routing = [
	include(gs_inner_routing, path=r'^/gs'),
	include(ws_inner_routing, path=r'^/ws'),
]
