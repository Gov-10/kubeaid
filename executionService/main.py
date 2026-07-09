from fastapi import FastAPI, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from fastapi.responses import Response 
from database import Execution, sessionLocal
import os, json, uuid, time, logging
from prometheus_client import Counter, Histogram, Gauge, CONTENT_TYPE_LATEST, generate_latest 
from kafka import KafkaProducer
from dotenv import load_dotenv()
BOOTSTRAP = os.getenv("BOOTSTRAP")
app = FastAPI()
REQUEST_COUNT = Counter("request_count", "Total request count", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("request_latency", "Total request latency", ["method", "endpoint"])
producer = KafkaProducer(bootstrap_servers= BOOTSTRAP, value_serializer= lambda x: json.dumps(x).encode("utf-8"))
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("execution")
def get_db():
    db = sessionLocal()
    try:
        yield db 
    finally:
        db.close()

@app.middleware("http")
def middle(request: Request, call_next):
    if request.url.path == "/metrics":
        return call_next(request)
    start = time.time()
    resp = call_next(request)
    process_time = time.time() - start
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=resp.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)
    return resp

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def check():
    return {"status": "Running"}

@app.get("/dbcheck")
def db_check(db: Session=Depends(get_db)):
    db_status = "up"
    try:
        db.execute(text('SELECT 1'))
    except Exception as e:
        logger.error(json.dumps({"event": "database_down", "error": str(e)}))
        db_status ="down"
    return {"db_status": db_status}

@app.post("/execute")
def exec(payload: ExecuteSchema, db:Session=Depends(get_db)):
    template_id, execution = payload.template_id, payload.execution
    db_note = Execution(template_id=template_id, execution=execution, task_id = str(uuid.uuid4()))
    db.add(db_note)
    try:
        db.commit()
        logger.info(json.dumps({"event": "execution_received", "task_id": db_note.task_id}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event": "database_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="database error")
    db.refresh(db_note)
    event = {"template_id": template_id, "task_id": db_note.task_id}
    producer.send("execution-send", key=str(db_note.task_id).encode(), value=event)
    producer.flush()
    logger.info(json.dumps({"event": "pushed_to_kafka", "task_id": db_note.task_id}))
    return {"messaged": "queued"}
