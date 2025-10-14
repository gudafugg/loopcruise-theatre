# -*- coding: utf-8 -*-
"""
对话管理API接口
提供对话历史查询、导出、统计等功能
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger

from app.database.sqlite_storage import storage
from app.database.models import ConversationMessage, ConversationSession

router = APIRouter()


class ConversationHistoryResponse(BaseModel):
    """对话历史响应"""
    session_id: str
    messages: List[dict]
    total_count: int
    page_info: dict


class ConversationStatsResponse(BaseModel):
    """对话统计响应"""
    session_id: str
    stats: dict
    session_info: dict


@router.get("/history/{session_id}")
async def get_conversation_history(
    session_id: str,
    limit: int = Query(50, description="每页消息数量", ge=1, le=200),
    offset: int = Query(0, description="偏移量", ge=0)
) -> ConversationHistoryResponse:
    """
    获取对话历史
    
    参数:
    - session_id: 会话ID
    - limit: 每页消息数量 (1-200)
    - offset: 偏移量
    """
    try:
        # 确保数据库已初始化
        await storage.initialize()
        
        # 获取对话历史
        messages = await storage.get_conversation_history(session_id, limit, offset)
        
        # 获取总数统计
        stats = await storage.get_conversation_stats(session_id)
        total_count = stats.get('total_messages', 0)
        
        # 转换为字典格式
        message_dicts = [msg.to_dict() for msg in messages]
        
        return ConversationHistoryResponse(
            session_id=session_id,
            messages=message_dicts,
            total_count=total_count,
            page_info={
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            }
        )
        
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")


@router.get("/stats/{session_id}")
async def get_conversation_stats(session_id: str) -> ConversationStatsResponse:
    """
    获取对话统计信息
    """
    try:
        await storage.initialize()
        
        # 获取会话信息
        session = await storage.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取统计信息
        stats = await storage.get_conversation_stats(session_id)
        
        return ConversationStatsResponse(
            session_id=session_id,
            stats=stats,
            session_info=session.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取对话统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/sessions")
async def list_conversation_sessions(
    limit: int = Query(20, description="每页会话数量", ge=1, le=100),
    offset: int = Query(0, description="偏移量", ge=0)
) -> dict:
    """
    列出所有对话会话
    """
    try:
        await storage.initialize()
        
        sessions = await storage.list_sessions(limit, offset)
        session_dicts = [session.to_dict() for session in sessions]
        
        return {
            "sessions": session_dicts,
            "page_info": {
                "limit": limit,
                "offset": offset,
                "count": len(session_dicts)
            }
        }
        
    except Exception as e:
        logger.error(f"获取会话列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")


@router.get("/export/{session_id}")
async def export_conversation(session_id: str) -> dict:
    """
    导出完整对话记录
    """
    try:
        await storage.initialize()
        
        # 检查会话是否存在
        session = await storage.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取完整对话历史
        messages = await storage.get_conversation_history(session_id, limit=10000)
        stats = await storage.get_conversation_stats(session_id)
        
        export_data = {
            "export_info": {
                "session_id": session_id,
                "export_time": datetime.now().isoformat(),
                "total_messages": len(messages)
            },
            "session": session.to_dict(),
            "messages": [msg.to_dict() for msg in messages],
            "stats": stats
        }
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.delete("/session/{session_id}")
async def delete_conversation_session(session_id: str) -> dict:
    """
    删除对话会话和所有相关数据
    """
    try:
        await storage.initialize()
        
        # 检查会话是否存在
        session = await storage.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 删除会话
        success = await storage.delete_session(session_id)
        
        if success:
            return {"success": True, "message": f"会话 {session_id} 已删除"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_conversations(
    days: int = Query(30, description="保留天数", ge=1, le=365)
) -> dict:
    """
    清理旧的对话记录
    
    参数:
    - days: 保留最近N天的数据，删除更早的记录
    """
    try:
        await storage.initialize()
        
        deleted_count = await storage.cleanup_old_sessions(days)
        
        return {
            "success": True,
            "message": f"清理完成，删除了 {deleted_count} 个会话",
            "deleted_count": deleted_count,
            "retention_days": days
        }
        
    except Exception as e:
        logger.error(f"清理对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")


@router.get("/search/{session_id}")
async def search_conversation(
    session_id: str,
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, description="返回结果数量", ge=1, le=100)
) -> dict:
    """
    在对话历史中搜索关键词
    """
    try:
        await storage.initialize()
        
        # 获取所有消息
        all_messages = await storage.get_conversation_history(session_id, limit=1000)
        
        # 简单的关键词搜索
        matching_messages = []
        for msg in all_messages:
            if query.lower() in msg.content.lower():
                matching_messages.append(msg.to_dict())
                if len(matching_messages) >= limit:
                    break
        
        return {
            "session_id": session_id,
            "query": query,
            "matches": matching_messages,
            "total_matches": len(matching_messages)
        }
        
    except Exception as e:
        logger.error(f"搜索对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/summary/{session_id}")
async def get_conversation_summary(session_id: str) -> dict:
    """
    获取对话摘要
    """
    try:
        await storage.initialize()
        
        # 检查会话是否存在
        session = await storage.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取统计信息
        stats = await storage.get_conversation_stats(session_id)
        
        # 获取最近几条重要消息
        recent_messages = await storage.get_recent_context(session_id, max_messages=5)
        
        # 构建摘要
        summary = {
            "session_id": session_id,
            "session_info": {
                "script_title": session.script_title,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None
            },
            "stats": stats,
            "recent_highlights": [
                {
                    "speaker": msg.speaker_name,
                    "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                    "time": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in recent_messages[-3:] if msg.content.strip()
            ]
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取对话摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取摘要失败: {str(e)}")
