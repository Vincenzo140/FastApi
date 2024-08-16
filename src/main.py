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

app= fastApiObservability.get_api_application()

uvicorn_logger.error("Log analogado, Erro") 
uvicorn_logger.critical("Log Imparcial para a Aplicação")

@app.get("/")
def main():
    logger.info("Recuperando Main")
    return{"Hello World :)"}

@app.get('/data')
def get_system_date():
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("Recuperando Data")
    return {"date": current_date}

@app.get("/cpu")
def get_cpu_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    logger.info("Recuperando CPU")
    counterCPU.add(1)
    return {"cpu_usage": cpu_usage}

@app.get("/ram")
def get_ram_usage():
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    logger.debug("Recuperando RAM")
    return {"ram_usage": ram_usage}

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
            f"http://{TARGET_ONE_HOST}:8000/data",
            headers=headers,
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_TWO_HOST}:8000/cpu",
            headers=headers,
        )
    logging.info("Chain Finished")
    return {"path": "/chain"}


if __name__ == "__main__":

    logConfig = Logger(appName=APP_NAME, name=APP_NAME, level=logging.DEBUG)
    # logConfig.setLogFile(path=LOG_FILE)
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
    