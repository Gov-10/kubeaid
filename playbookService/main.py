from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import Response
import os, time, uuid, logging, json
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy.orm import Session
from sqlalchemy.text import 
from database import Template, sessionLocal
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
REQUEST_COUNT = Counter("total_requests", "Total requests http", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("request_latency", "Request latency", ["method", "endpoint"])
def get_db():
    db=sessionLocal()
    try:
        yield db 
    finally:
        db.close()

app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("playbook")
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


@app.get("/")
def chek():
    return {"status": "Running"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/dbcheck")
def db_chek(db:Session=Depends(get_db)):
    db_status = "up"
    try:
        db.execute(text('SELECT 1'))
    except Exception as e:
        db_status ="down"
    return {"db_status": db_status}

@app.post("/create")
def create_play(payload: CreateSchema, db:Session=Depends(get_db)):
    name, description, definition = payload.name, payload.description, payload.definition
    db_note = Template(name=name, description=description, definition=definition, template_id=str(uuid.uuid4())
    db.add(db_note)
    try:
        db.commit()
        logger.info(json.dumps({"event":"template_creation"})
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event" : "database_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="database error")
    db.refresh(db_note)
    return {"template_id": db_note.template}

@app.get("/templates/{temp_id}")
def get_temp(temp_id: str|None = None, db:Session=Depends(get_db)):
    if temp_id:
        temp = db.query(Template).filter(Template.template_id == temp_id).first()
        if not temp:
            logger.warning(json.dumps({"event": "template_id_not_found", "temp_id": temp_id}))
            raise HTTPException(status_code=404, detail="no template found")
        return {"template_id": temp.template_id, "name": temp.name, "description": temp.description, "created_at" : temp.created_at, "edited_at": temp.edited_at, "definition" : temp.definition}
    temps = db.query(Template).all()
    res =[]
    for temp in temps:
        te = {"template_id" : temp.template_id, "name" : temp.name, "description" : temp.description, "created_at": temp.created_at, "edited_at": temp.edited_at, "definition" : temp.definition}
        res.append(te)
    return te

@app.put("/templates/{temp_id})
def edit_temp(temp_id: str, payload: UpdateSchema, db:Session=Depends(get_db)):
    temp = db.query(Template).filter(Template.template_id == temp_id).first()
    if not temp:
        logger.warning(json.dumps({"event": "template_id_not_found", "temp_id": temp_id}))
        raise HTTPException(status_code=404, detail="no template found")
    for key, value in payload.items():
        setattr(temp, key, value)
    db.add(temp)
    try:
        db.commit()
        logger.info(json.dumps({"event": "template_updated", "temp_id": temp_id}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event" : "database_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="database error")
    db.refresh(temp)
    return {"message" : "updated"}

@app.delete("/templates/{temp_id})
def del_temp(temp_id: str, db:Session=Depends(get_db)):
    temp = db.query(Template).filter(Template.template_id == temp_id).first()
    if not temp:
        logger.warning(json.dumps({"event": "template_id_not_found", "temp_id": temp_id}))
        raise HTTPException(status_code=404, detail="no template found")
    db.delete(temp)
    try:
        db.commit()
        logger.info(json.dumps({"event": "template_deleted", "temp_id": temp_id}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event" : "database_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="database error")
    return {"message" : "deleted"}


