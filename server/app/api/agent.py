# -*- coding: utf-8 -*-
"""
AI Agent API接口
整合AI Agent功能到现有的SSE流式系统中
"""

import asyncio
import json
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger

from app.agents.ollama_agent import OllamaAgent
from app.agents.memory_agent import MemoryEnhancedAgent
from app.agents.base_agent import UserInput
from app.api.stream import _hub  # 导入现有的SSE hub
from app.database.sqlite_storage import storage

router = APIRouter()

# Agent实例管理（现在使用带记忆的Agent）
_agents: Dict[str, MemoryEnhancedAgent] = {}


class LoadScriptRequest(BaseModel):
    """加载剧本请求"""
    session_id: str
    script_text: str
    model_name: Optional[str] = "qwen2.5:7b"
    ollama_url: Optional[str] = "http://localhost:11434"


class ChatRequest(BaseModel):
    """聊天请求"""
    session_id: str
    message: str
    stream: Optional[bool] = True


class AgentStatusResponse(BaseModel):
    """Agent状态响应"""
    session_id: str
    status: str
    agent_name: str
    script_loaded: bool
    script_title: Optional[str] = None


async def _get_or_create_agent(session_id: str, 
                             model_name: str = "qwen2.5:7b",
                             ollama_url: str = "http://localhost:11434") -> MemoryEnhancedAgent:
    """获取或创建带记忆的Agent实例"""
    if session_id not in _agents:
        agent = MemoryEnhancedAgent(model_name=model_name, ollama_url=ollama_url)
        await agent.initialize_session(session_id)  # 初始化会话
        _agents[session_id] = agent
        logger.info(f"为会话 {session_id} 创建新的带记忆Agent实例")
    return _agents[session_id]


@router.post("/load_script")
async def load_script(request: LoadScriptRequest) -> dict:
    """
    加载剧本到指定会话的Agent
    
    Body:
    {
        "session_id": "sess_xxx",
        "script_text": "完整的剧本文本...",
        "model_name": "qwen2.5:7b",  // 可选
        "ollama_url": "http://localhost:11434"  // 可选
    }
    """
    try:
        # 创建或获取Agent实例
        agent = await _get_or_create_agent(
            request.session_id, 
            request.model_name, 
            request.ollama_url
        )
        
        # 确保SSE会话存在
        _hub.create_session(request.session_id)
        
        # 向前端发送加载状态
        await _hub.publish(request.session_id, {
            "type": "agent_status",
            "data": {"status": "loading_script", "message": "正在解析剧本..."}
        })
        
        # 加载剧本
        success = await agent.load_script(request.script_text)
        
        if success:
            # 发送成功状态
            await _hub.publish(request.session_id, {
                "type": "agent_status",
                "data": {
                    "status": "script_loaded",
                    "message": f"剧本加载成功：{agent.script_context.title}",
                    "script_info": {
                        "title": agent.script_context.title,
                        "characters": agent.script_context.characters,
                        "setting": agent.script_context.setting
                    }
                }
            })
            
            return {
                "success": True,
                "message": "剧本加载成功",
                "script_title": agent.script_context.title
            }
        else:
            # 发送失败状态
            await _hub.publish(request.session_id, {
                "type": "agent_status", 
                "data": {"status": "error", "message": "剧本加载失败"}
            })
            
            raise HTTPException(status_code=400, detail="剧本加载失败")
            
    except Exception as e:
        logger.error(f"加载剧本时出错: {e}")
        
        # 发送错误状态
        if _hub.has_session(request.session_id):
            await _hub.publish(request.session_id, {
                "type": "agent_status",
                "data": {"status": "error", "message": f"发生错误: {str(e)}"}
            })
        
        raise HTTPException(status_code=500, detail=f"内部错误: {str(e)}")


@router.post("/chat")
async def chat(request: ChatRequest) -> dict:
    """
    与Agent聊天
    
    Body:
    {
        "session_id": "sess_xxx",
        "message": "用户消息",
        "stream": true  // 是否启用流式响应
    }
    """
    try:
        # 检查Agent是否存在
        if request.session_id not in _agents:
            raise HTTPException(status_code=404, detail="Agent未初始化，请先加载剧本")
        
        agent = _agents[request.session_id]
        
        # 检查剧本是否已加载
        if not agent.script_context:
            raise HTTPException(status_code=400, detail="请先加载剧本")
        
        # 确保SSE会话存在
        _hub.create_session(request.session_id)
        
        # 创建用户输入对象
        user_input = UserInput(
            text=request.message,
            session_id=request.session_id
        )
        
        if request.stream:
            # 流式响应
            await _hub.publish(request.session_id, {
                "type": "ai_thinking",
                "data": {"message": "AI正在思考中..."}
            })
            
            # 启动流式生成任务
            asyncio.create_task(_stream_ai_response(agent, user_input))
            
            return {"success": True, "message": "开始流式响应"}
        else:
            # 单次响应（使用带记忆的方法）
            response = await agent.generate_response_with_memory(user_input)
            
            # 通过SSE发送响应
            await _hub.publish(request.session_id, {
                "type": "npc",
                "data": {
                    "speaker_id": response.speaker_id,
                    "text": response.text,
                    "emotion": response.emotion,
                    "confidence": response.confidence
                }
            })
            
            return {
                "success": True,
                "response": {
                    "speaker_id": response.speaker_id,
                    "text": response.text
                }
            }
            
    except Exception as e:
        logger.error(f"聊天时出错: {e}")
        
        # 发送错误消息
        if _hub.has_session(request.session_id):
            await _hub.publish(request.session_id, {
                "type": "error",
                "data": {"message": f"聊天出错: {str(e)}"}
            })
        
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")


async def _stream_ai_response(agent: MemoryEnhancedAgent, user_input: UserInput):
    """异步处理带记忆的流式AI响应"""
    try:
        full_response = ""
        
        # 开始流式生成（使用带记忆的方法）
        async for chunk in agent.stream_response_with_memory(user_input):
            if chunk.strip():
                full_response += chunk
                
                # 实时发送部分响应
                await _hub.publish(user_input.session_id, {
                    "type": "ai_stream",
                    "data": {
                        "chunk": chunk,
                        "full_text": full_response
                    }
                })
        
        # 最终响应已经在stream_response_with_memory中保存到数据库
        # 这里只需要发送完成信号
        await _hub.publish(user_input.session_id, {
            "type": "stream_complete",
            "data": {"message": "AI响应完成"}
        })
        
    except Exception as e:
        logger.error(f"流式响应处理失败: {e}")
        await _hub.publish(user_input.session_id, {
            "type": "error",
            "data": {"message": f"AI响应失败: {str(e)}"}
        })


@router.get("/status/{session_id}")
async def get_agent_status(session_id: str) -> AgentStatusResponse:
    """获取Agent状态"""
    if session_id not in _agents:
        return AgentStatusResponse(
            session_id=session_id,
            status="not_initialized",
            agent_name="OllamaAgent",
            script_loaded=False
        )
    
    agent = _agents[session_id]
    script_loaded = agent.script_context is not None
    
    return AgentStatusResponse(
        session_id=session_id,
        status="ready" if script_loaded else "initialized",
        agent_name=agent.name,
        script_loaded=script_loaded,
        script_title=agent.script_context.title if script_loaded else None
    )


@router.delete("/session/{session_id}")
async def cleanup_agent_session(session_id: str) -> dict:
    """清理Agent会话"""
    if session_id in _agents:
        agent = _agents[session_id]
        await agent.close()
        del _agents[session_id]
        logger.info(f"已清理会话 {session_id} 的Agent实例")
    
    # 同时清理SSE会话
    _hub.close(session_id)
    
    return {"success": True, "message": f"会话 {session_id} 已清理"}


@router.get("/models")
async def list_available_models() -> dict:
    """列出可用的Ollama模型（需要连接Ollama服务）"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    return {"success": True, "models": models}
                else:
                    return {"success": False, "message": "无法连接Ollama服务"}
    except Exception as e:
        return {"success": False, "message": f"获取模型列表失败: {str(e)}"}
