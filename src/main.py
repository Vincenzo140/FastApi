from lib_fastapi.lib_fastapi import FastApiObservability
from prometheus_client import Counter
from lib_fastapi.lib_log import Logger
from lib_fastapi.lib_instrumentation import Instrumentation

from lib_fastapi.lib_metrics import Metrics
from datetime import datetime
import logging
import uvicorn
import psutil
import os
from fastapi import FastAPI, Response, Header
import httpx


EXPOSE_PORT = os.environ.get("EXPOSE_PORT", 8000)
APP_NAME = os.environ.get("APP_NAME", "app")
TARGET_ONE_HOST = os.environ.get("TARGET_ONE_HOST", "app-b")
TARGET_TWO_HOST = os.environ.get("TARGET_TWO_HOST", "app-c")
METRICS_EXPORTER_URL = os.environ.get("METRICS_EXPORTER_URL")
TRACES_EXPORTER_URL = os.environ.get("TRACES_EXPORTER_URL")
LOGS_EXPORTER_URL= os.environ.get("LOGS_EXPORTER_URL")
APP_NAME= os.environ.get("APP_NAME")
APP_HOST= os.environ.get("APP_HOST")
APP_PORT= os.environ.get("APP_PORT")
APP_VERSION= os.environ.get("APP_VERSION")
LOG_FILE = os.environ.get("LOG_FILE")

fastApiObservability= FastApiObservability(path="", name=APP_NAME, version=APP_VERSION)
metrics = Metrics()
metrics.setMetricsProvider(appName=APP_NAME,url=METRICS_EXPORTER_URL)
metrics.setMeter()
counterCPU = metrics.createCounter("CounterCPU")

logger = logging.getLogger(__name__)
uvicorn_logger = logging.getLogger('uvicorn')
uvicorn_logger.setLevel(logging.ERROR)
uvicorn_logger.setLevel(logging.CRITICAL)

app = fastApiObservability.get_api_application()

uvicorn_logger.error("Log analogado, Erro") 
uvicorn_logger.critical("Log Imparcial para a Aplicação")

# Novos Endpoints
@app.get("/uptime")
def get_system_uptime():
    uptime_seconds = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    logger.info("Recuperando uptime do sistema")
    return {"uptime": str(uptime_seconds)}

@app.get("/disk")
def get_disk_usage():
    disk_usage = psutil.disk_usage('/')
    logger.info("Recuperando uso de disco")
    return {"total_disk_space": disk_usage.total, "used_disk_space": disk_usage.used, "free_disk_space": disk_usage.free, "disk_usage_percentage": disk_usage.percent}

@app.get("/network")
def get_network_io():
    net_io = psutil.net_io_counters()
    logger.info("Recuperando informações de rede")
    return {"bytes_sent": net_io.bytes_sent, "bytes_received": net_io.bytes_recv, "packets_sent": net_io.packets_sent, "packets_received": net_io.packets_recv}


@app.get("/chain")
async def chain(response: Response):
    headers = {}  # Passa o header traceparent diretamente
    logging.critical(headers)

    async with httpx.AsyncClient() as client:
        await client.get(
            "http://localhost:8000/",
            headers=headers,
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_ONE_HOST}:8000/uptime",
            headers=headers,
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_TWO_HOST}:8000/disk",
            headers=headers,
        )
        
    logging.info("Chain Finished")
    return {"path": "/chain"}


if __name__ == "__main__":
    logConfig = Logger(appName=APP_NAME, name=APP_NAME, level=logging.DEBUG)
    logConfig.setLogExporter(url=LOGS_EXPORTER_URL)
    logConfig.setLogConsole()
    logConfig.setFormatter()
    logConfig.setBasicConfig()
    fastApiObservability.setInstrumentorTraces(grpc=True, url=TRACES_EXPORTER_URL)
    fastApiObservability.setMetricsPrometheus()

    uvicorn.run(
        app,
        host=APP_HOST,
        port=int(APP_PORT),
        log_config=logConfig.getConfig()
    )

    