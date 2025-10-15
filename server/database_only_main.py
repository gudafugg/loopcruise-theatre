"""
数据库专用API服务 - 仅提供数据库访问功能
不包含AI Agent相关功能，专为协作者使用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import conversation
from app.database.sqlite_storage import storage

# 初始化数据库
storage.init_database()

app = FastAPI(
    title="LoopcruiseTheatre Database API", 
    version="1.0.0",
    description="数据库访问专用API - 不包含AI功能"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 协作者可能从不同地址访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 仅注册数据库相关路由
app.include_router(conversation.router, prefix="/api/v1/conversation", tags=["conversation"])

@app.get("/")
async def root():
    return {
        "message": "LoopcruiseTheatre Database API",
        "version": "1.0.0",
        "description": "数据库访问专用API - 仅提供对话历史查询功能",
        "endpoints": {
            "conversations": "/api/v1/conversation/",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        stats = storage.get_conversation_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # 使用不同端口避免冲突
