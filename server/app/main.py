from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import stream, agent, conversation

app = FastAPI(title="LoopcruiseTheatre API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stream.router, prefix="/api/v1/stream", tags=["stream"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])
app.include_router(conversation.router, prefix="/api/v1/conversation", tags=["conversation"])