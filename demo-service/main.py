import time
import logging
from fastapi import FastAPI, HTTPException, Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("demo-service")

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI(title="Demo Service")

resource = Resource.create({"service.name": "demo-service"})
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

FastAPIInstrumentor.instrument_app(app)

is_broken = False


@app.get("/")
async def root():
    global is_broken
    if is_broken:
        logger.error("High error rate triggered by fault injection!")
        raise HTTPException(status_code=500, detail="Internal Server Error - Fault Injected")
    return {"status": "ok", "message": "Demo service operational"}


@app.post("/break")
async def toggle_break(enable: bool = True):
    global is_broken
    is_broken = enable
    status = "broken (returning 500 errors)" if is_broken else "healthy"
    logger.info("Demo service state changed: %s", status)
    return {"is_broken": is_broken, "status": status}
