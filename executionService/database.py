from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os, uuid
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine =create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class Execution(Base):
    __tablename__ ="executions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(String)
    execution = Column(JSON, default ={})
    created_at = Column(DateTime, default=datetime.utcnow)
    task_id = Column(String, default=str(uuid.uuid4()))

Base.metadata.create_all(bind=engine)
