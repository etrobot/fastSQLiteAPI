from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .routes import query
from .config import get_settings
from .database import initialize_db
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
settings = get_settings()

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 认证中间件
async def verify_token(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(' ')[1]
    if token != settings.auth_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 注册路由
app.include_router(
    query.router,
    prefix="/api",
    dependencies=[Depends(verify_token)]
)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Attempting to initialize database at: {settings.db_path}")
    try:
        await initialize_db(settings.db_path)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
    if isinstance(exc, HTTPException):
        raise exc
    return {"error": "Internal Server Error"}

@app.get("/")
async def root():
    return {"message": "API is running"} 