import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from infrastructure import kubernetes


class FastAPIServer:

    def __init__(self, webserver_config: dict = None):
        swagger_ui_init_oauth = {"clientId": "python-client", "appName": "KeyCloak Auth test"}
        self.app = FastAPI(swagger_ui_init_oauth=swagger_ui_init_oauth)
        self.port = 80 if webserver_config is None else webserver_config['port']
        self.app.add_middleware(CORSMiddleware,
                                allow_origins='*',
                                allow_credentials=True,
                                allow_methods=["*"],
                                allow_headers=["*"], )
        self.__setup_routes__()

    def get(self) -> FastAPI:
        return self.app

    def startup_event(self, callback):
        self.app.add_event_handler("startup", callback)

    def shutdown_event(self, callback):
        self.app.add_event_handler("shutdown", callback)

    def register_endpoint(self, relative_url: str, app, name: str = None):
        if relative_url.startswith('http'):
            raise ValueError(f"Given url is not relative! Url: {relative_url}")

        if name is None:
            self.app.add_route(relative_url, app)
        else:
            self.app.add_route(relative_url, app, name)

    def __setup_routes__(self):
        self.app.include_router(kubernetes.router, prefix='/_status')

    def start(self):
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, loop='asyncio', forwarded_allow_ips='*')
