from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPgrpcExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPhttpExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

class Instrumentation():

    def setting_otlp(self,app: FastAPI = None, 
                     appName: str = "app", 
                     url = "http://localhost:4317",
                     grpc: bool = True) -> None:
        
        resource = Resource.create(attributes={
            "service.name": appName,
            "compose_service": appName
        })

        tracer = TracerProvider(resource=resource)
        
        if grpc:
            logger.debug("Configurando OTLP GRPC Exporter")
            tracer.add_span_processor(BatchSpanProcessor(OTLPgrpcExporter(endpoint=url)))
        else:
            logger.debug("Configurando OTLP HTTP Exporter")
            tracer.add_span_processor(BatchSpanProcessor(OTLPhttpExporter(endpoint=url)))
            
        trace.set_tracer_provider(tracer)
        FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)