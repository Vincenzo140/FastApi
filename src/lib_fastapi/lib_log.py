from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
import logging

LOG_FORMAT_DEFAULT = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"

class EndpointFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find('GET /metrics') == -1

class Logger():
    
    def __init__(self, appName: str = "", name: str ="", level=None):
        self.appName = appName
        self.name = name
        self.level = level
        self.handlers = []
        self.formatter = ""
    
    def getConfig(self):
              
        return logging.basicConfig(level=self.level,
                                   handlers=self.handlers,
                                   format=self.formatter)
        
        # self.logger.addFilter(EndpointFilter())
            
    def getExporterHandler(self, url):
        logger_provider = LoggerProvider(
            resource=Resource.create(
            {
                "service.name": self.appName,
                "service.instance.id": self.appName,
            }),
        )
        set_logger_provider(logger_provider)
        
        otlp_exporter = OTLPLogExporter(endpoint=url, insecure=True)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

        return LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    
    def getFileHandler(self, path):
        return logging.FileHandler(path)

    def getConsoleHandler(self):
        return logging.StreamHandler()
        
    def setLogFile(self, path: str= '/log.log'):
        self.handlers.append(self.getFileHandler(path))
        
    def setLogExporter(self, url: str = 'http://localhost:4317'):
        self.handlers.append(self.getExporterHandler(url))
        
    def setLogConsole(self):
        self.handlers.append(self.getConsoleHandler())

    def setFormatter(self, formatter: str=LOG_FORMAT_DEFAULT):
        self.formatter = formatter
    
    def setBasicConfig(self):
        logging.basicConfig(level=self.level,
                            handlers=self.handlers,
                            format=self.formatter)