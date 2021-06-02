# from fastapi import FastAPI
# from starlette.middleware.cors import CORSMiddleware

# # from app.api.api_v1.api import api_router
# from core.config import settings

# app = FastAPI(
#     title=settings.PROJECT_NAME
# )

# # Set all CORS enabled origins
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(api_router, prefix=settings.API_V1_STR)

from typing import List
# from databases import Database
import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel

# SQLAlchemy specific code, as with any other app
# DATABASE_URL = "sqlite:///./test.db"
DATABASE_URL = "postgresql://postgres:12345678@database-2.ckgekixw3q0p.us-east-1.rds.amazonaws.com/postgres"
# DATABASE_URL = "postgresql://postgres:12345678@spring-quest:5432"


database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
)


# engine = sqlalchemy.create_engine(
#     DATABASE_URL, connect_args={"check_same_thread": False}
# )
# metadata.create_all(engine)


class NoteIn(BaseModel):
    text: str


class Note(BaseModel):
    id: int
    text: str


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/notes/", response_model=List[Note])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)


@app.post("/notes/", response_model=Note)
async def create_note(note: NoteIn):
    query = notes.insert().values(text=note.text )
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}
