from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv

from .database import Base, engine
from .routers import devices, inspections
from .schemas import MetadataResponse, MAINSTREAM_BRANDS, APPEARANCE_GRADES, FUNCTION_ITEMS_LIST

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=os.getenv("PROJECT_NAME", "回收门店设备管理系统"),
    description="手机回收门店设备档案与质检记录管理系统",
    version="1.0.0",
)

cors_origins = os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:5173"]')
import json
try:
    origins = json.loads(cors_origins)
except (json.JSONDecodeError, TypeError):
    origins = ["http://localhost:5173", "http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = os.getenv("API_V1_PREFIX", "/api/v1")

app.include_router(devices.router, prefix=api_prefix, tags=["设备档案"])
app.include_router(inspections.router, prefix=api_prefix, tags=["质检记录"])


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.get(f"{api_prefix}/metadata", response_model=MetadataResponse, tags=["元数据"])
def get_metadata():
    return {
        "mainstream_brands": sorted(list(MAINSTREAM_BRANDS)),
        "appearance_grades": sorted(list(APPEARANCE_GRADES)),
        "function_items": [{"key": item, "label": item} for item in FUNCTION_ITEMS_LIST],
    }
