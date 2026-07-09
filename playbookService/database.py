from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import os, uuid
from datetime import datetime 
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    edited_at = Column(DateTime, default=datetime.utcnow)
    definition = Column(JSON, default={})
    template_id = Column(String, default=str(uuid.uuid4()))

Base.metadata.create_all(bind=engine)
