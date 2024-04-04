import time
import datetime
import threading
import schedule
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client.openmetrics.exposition import (CONTENT_TYPE_LATEST,
                                                      generate_latest)
from starlette.responses import Response
from prometheus_client import REGISTRY, pushadd_to_gateway

from lib_fastapi.lib_prometheus import PrometheusMiddleware
from lib_fastapi.lib_instrumentation import Instrumentation


logger = logging.getLogger(__name__)

class FastApiObservability:

    def __init__(self, path: str="", name: str="app", version: str="0.0.1"):
        
        self.name = name
        self.version = version
        self.path = path
        
        self.app = FastAPI(
            title=self.name,
            version=self.version,
            docs_url=f"{self.path}/docs/",
            openapi_url="/openapi.json"
        )

        # self.app.router.redirect_slashes = False

        # self.app.add_middleware(
        #     CORSMiddleware,
        #     allow_origins=["*"],
        #     allow_credentials=True,
        #     allow_methods=["*"],
        #     allow_headers=["*"],
        # )

    def setMetricsPrometheus(self):
        self.app.add_middleware(PrometheusMiddleware, app_name=self.name)
        self.app.add_route("/metrics", self.metrics)
        
        @self.app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            response.headers['response_time'] = str(
                datetime.timedelta(seconds=(time.time() - start_time))
            )
            return response
        
    def setExporterPushGateway(self, url: str= 'http://localhost:5000'):
        self.urlPushGateway = url
        schedule.every(10).seconds.do(self.send_metrics)
        metrics_thread = threading.Thread(target=self.send_metrics_timer)
        metrics_thread.daemon = True
        metrics_thread.start()
    
    def setInstrumentorTraces(self, url: str="http://localhost:4317", grpc: bool = True):
        Instrumentation().setting_otlp(app=self.app, appName=self.name, grpc=grpc, url=url)
               
    def get_api_application(self):
        return self.app

    def metrics(self, request: Request) -> Response:
        return Response(generate_latest(REGISTRY), headers={"Content-Type": CONTENT_TYPE_LATEST})
    
    def send_metrics(self):
        try:
            pushadd_to_gateway(self.urlPushGateway, job=self.name, registry=REGISTRY)
        except Exception as e:
            logging.error(f"Error send metrics to pushGateway: {e}")
            
    def send_metrics_timer(self):
        while True:
            schedule.run_pending()
            time.sleep(1)