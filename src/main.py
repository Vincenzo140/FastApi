import logging
import os
import random
from datetime import datetime
from typing import Optional

import httpx
import psutil
import uvicorn
from faker import Faker
from fastapi import FastAPI, Header, Response
from prometheus_client import Counter

from lib_fastapi.lib_fastapi import FastApiObservability
from lib_fastapi.lib_instrumentation import Instrumentation
from lib_fastapi.lib_log import Logger
from lib_fastapi.lib_metrics import Metrics

EXPOSE_PORT = os.environ.get("EXPOSE_PORT", 8000)
APP_NAME = os.environ.get("APP_NAME", "app")
TARGET_ONE_HOST = os.environ.get("TARGET_ONE_HOST", "app-b")
TARGET_TWO_HOST = os.environ.get("TARGET_TWO_HOST", "app-c")
METRICS_EXPORTER_URL = os.environ.get("METRICS_EXPORTER_URL")
TRACES_EXPORTER_URL = os.environ.get("TRACES_EXPORTER_URL")
LOGS_EXPORTER_URL = os.environ.get("LOGS_EXPORTER_URL")
APP_NAME = os.environ.get("APP_NAME")
APP_HOST = os.environ.get("APP_HOST")
APP_PORT = os.environ.get("APP_PORT")
APP_VERSION = os.environ.get("APP_VERSION")
LOG_FILE = os.environ.get("LOG_FILE")


fastApiObservability = FastApiObservability(path="", name=APP_NAME, version=APP_VERSION)
metrics = Metrics()
metrics.setMetricsProvider(appName=APP_NAME, url=METRICS_EXPORTER_URL)
metrics.setMeter()
counterCPU = metrics.createCounter("CounterCPU")

app = fastApiObservability.get_api_application()
fake = Faker()
logger = logging.getLogger(__name__)
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.ERROR)
uvicorn_logger.setLevel(logging.CRITICAL)


uvicorn_logger.error("esse log não irá aparecer, pq ele é um erro")
uvicorn_logger.critical("esse log não irá aparecer pq é inútil")


@app.get("/desculpas")
def desculpas():
    array_de_desculpas = [
        "Meu cachorro comeu meu laptop.",
        "Fui abduzido por alienígenas e só voltei agora.",
        "Desculpe, minha cama estava muito quente e confortável.",
        "Minha internet foi sequestrada pelos gremlins.",
        "Acidentalmente me inscrevi em um curso de malabarismo de facas.",
        "Estava ocupado tentando decifrar os enigmas da pirâmide de Gizé.",
        "Fui convocado para uma missão ultra-secreta da CIA.",
        "Estava testando a teoria da relatividade de Einstein na prática.",
        "Tive uma epifania e decidi viver como um eremita nas montanhas.",
        "Fui convidado para uma festa no submarino do Capitão Nemo.",
        "Descobri uma caverna secreta e fiquei explorando por dias.",
        "Acordei em uma realidade alternativa onde as aulas são opcionais.",
        "Meu clone foi à aula no meu lugar, mas acabou se perdendo.",
        "Estava participando de uma maratona de cochilos.",
        "Tive que resolver uma disputa entre unicórnios e dragões.",
        "Fui convocado para uma batalha épica de rock-paper-scissors.",
        "Estava em uma reunião com minha equipe de super-heróis.",
        "Descobri um portal para Nárnia e fiquei preso lá por um tempo.",
        "Me transformei em um gato e não consegui abrir a porta para sair.",
        "Tive que salvar o mundo em um videogame.",
        "Estava em uma maratona de memes e perdi a noção do tempo.",
        "Fui recrutado para a Liga dos Vingadores.",
        "Desculpe, fui hipnotizado por um hipnotizador hipnótico.",
        "Tive que lidar com uma invasão de patos zumbis no meu quintal.",
        "Meu despertador virou um ninja e desligou sozinho.",
        "Estava perseguindo o coelho branco em direção à toca do País das Maravilhas.",
        "Fui convocado para uma batalha de dança com o Darth Vader.",
        "Desculpe, estava tentando decifrar a língua dos pássaros.",
        "Estava testando uma máquina do tempo e perdi a noção do presente.",
        "Tive que assistir ao meu programa de TV favorito - O Telescópio dos Exoplanetas.",
    ]
    logger.debug("gerando_desculpas")
    return random.choice(array_de_desculpas)


@app.get("/data")
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


@app.get("/dados_invalidos")
async def dados_invalidos():
    dados_falsos = {
        "name": fake.name(),
        "stack": fake.job(),
        "endereco": fake.address(),
        "email": fake.email(),
        # Adicione mais campos conforme necessário
    }
    logger.debug("gerando dados falsos")
    return dados_falsos


@app.get("/chain")
async def chain(response: Response, traceparent: Optional[str] = Header(None)):
    headers = {"traceparent": traceparent}  # Passa o header traceparent diretamente
    logging.critical(headers)

    async with httpx.AsyncClient() as client:
        await client.get(
            "http://localhost:8000/",
            headers=headers,
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_ONE_HOST}:8000/io_task",
            headers=headers,
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_TWO_HOST}:8000/cpu_task",
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
    # fastApiObservability.setMetricsPrometheus()
    # fastApiObservability.setExporterPushGateway(url=METRICS_EXPORTER_URL)

    uvicorn.run(
        app, host=APP_HOST, port=int(APP_PORT), log_config=logConfig.getConfig()
    )
