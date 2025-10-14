# -*- coding: utf-8 -*-
"""
SQLite数据库存储实现
本地轻量级数据库，适合单机部署
"""

import sqlite3
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from loguru import logger

from .models import ConversationMessage, ConversationSession, ConversationSummary


class SQLiteConversationStorage:
    """基于SQLite的对话存储实现"""
    
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = Path(db_path)
        self._initialized = False
        
    async def initialize(self):
        """初始化数据库和表结构"""
        if self._initialized:
            return
        
        # 确保数据库目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建表结构
        await self._create_tables()
        self._initialized = True
        logger.info(f"SQLite数据库初始化完成: {self.db_path}")
    
    async def _execute_query(self, query: str, params: tuple = (), fetch: bool = False):
        """执行SQL查询（异步封装）"""
        def _sync_execute():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # 支持字典式访问
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
        
        # 在线程池中执行同步数据库操作
        return await asyncio.get_event_loop().run_in_executor(None, _sync_execute)
    
    async def _create_tables(self):
        """创建数据库表"""
        
        # 对话会话表
        await self._execute_query("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                session_id TEXT PRIMARY KEY,
                script_title TEXT,
                script_content TEXT,
                agent_model TEXT,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT
            )
        """)
        
        # 对话消息表
        await self._execute_query("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                message_type TEXT,
                role TEXT,
                speaker_name TEXT,
                content TEXT,
                metadata TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (session_id)
            )
        """)
        
        # 对话总结表
        await self._execute_query("""
            CREATE TABLE IF NOT EXISTS conversation_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                summary_content TEXT,
                message_count INTEGER,
                start_time TEXT,
                end_time TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (session_id)
            )
        """)
        
        # 创建索引以提高查询性能
        await self._execute_query("CREATE INDEX IF NOT EXISTS idx_messages_session_time ON conversation_messages (session_id, created_at)")
        await self._execute_query("CREATE INDEX IF NOT EXISTS idx_sessions_updated ON conversation_sessions (updated_at)")
    
    async def save_session(self, session: ConversationSession) -> bool:
        """保存或更新会话信息"""
        try:
            session_data = session.to_dict()
            
            await self._execute_query("""
                INSERT OR REPLACE INTO conversation_sessions 
                (session_id, script_title, script_content, agent_model, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data['session_id'],
                session_data['script_title'],
                session_data['script_content'],
                session_data['agent_model'],
                session_data['created_at'],
                session_data['updated_at'],
                session_data['metadata']
            ))
            
            logger.info(f"会话已保存: {session.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """获取会话信息"""
        try:
            rows = await self._execute_query("""
                SELECT * FROM conversation_sessions WHERE session_id = ?
            """, (session_id,), fetch=True)
            
            if rows:
                row_data = dict(rows[0])
                return ConversationSession.from_dict(row_data)
            return None
            
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            return None
    
    async def save_message(self, message: ConversationMessage) -> Optional[int]:
        """保存对话消息"""
        try:
            message_data = message.to_dict()
            
            await self._execute_query("""
                INSERT INTO conversation_messages 
                (session_id, message_type, role, speaker_name, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                message_data['session_id'],
                message_data['message_type'],
                message_data['role'],
                message_data['speaker_name'],
                message_data['content'],
                message_data['metadata'],
                message_data['created_at']
            ))
            
            # 获取插入的ID
            rows = await self._execute_query("SELECT last_insert_rowid()", fetch=True)
            message_id = rows[0][0] if rows else None
            
            logger.debug(f"消息已保存: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"保存消息失败: {e}")
            return None
    
    async def get_conversation_history(self, session_id: str, limit: int = 50, offset: int = 0) -> List[ConversationMessage]:
        """获取对话历史"""
        try:
            rows = await self._execute_query("""
                SELECT * FROM conversation_messages 
                WHERE session_id = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (session_id, limit, offset), fetch=True)
            
            messages = []
            for row in rows:
                row_data = dict(row)
                messages.append(ConversationMessage.from_dict(row_data))
            
            # 按时间正序返回（最早的在前）
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    async def get_recent_context(self, session_id: str, max_messages: int = 10) -> List[ConversationMessage]:
        """获取最近的对话上下文（用于AI理解）"""
        return await self.get_conversation_history(session_id, limit=max_messages)
    
    async def save_summary(self, summary: ConversationSummary) -> Optional[int]:
        """保存对话总结"""
        try:
            summary_data = summary.to_dict()
            
            await self._execute_query("""
                INSERT INTO conversation_summaries 
                (session_id, summary_content, message_count, start_time, end_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                summary_data['session_id'],
                summary_data['summary_content'],
                summary_data['message_count'],
                summary_data['start_time'],
                summary_data['end_time'],
                summary_data['created_at']
            ))
            
            rows = await self._execute_query("SELECT last_insert_rowid()", fetch=True)
            summary_id = rows[0][0] if rows else None
            
            logger.info(f"对话总结已保存: {summary_id}")
            return summary_id
            
        except Exception as e:
            logger.error(f"保存对话总结失败: {e}")
            return None
    
    async def get_conversation_stats(self, session_id: str) -> Dict[str, Any]:
        """获取对话统计信息"""
        try:
            # 消息数量统计
            rows = await self._execute_query("""
                SELECT COUNT(*) as total_messages,
                       COUNT(CASE WHEN message_type = 'user' THEN 1 END) as user_messages,
                       COUNT(CASE WHEN message_type = 'assistant' THEN 1 END) as ai_messages,
                       MIN(created_at) as first_message,
                       MAX(created_at) as last_message
                FROM conversation_messages 
                WHERE session_id = ?
            """, (session_id,), fetch=True)
            
            if rows:
                stats = dict(rows[0])
                return {
                    'total_messages': stats['total_messages'],
                    'user_messages': stats['user_messages'], 
                    'ai_messages': stats['ai_messages'],
                    'first_message': stats['first_message'],
                    'last_message': stats['last_message']
                }
            return {}
            
        except Exception as e:
            logger.error(f"获取对话统计失败: {e}")
            return {}
    
    async def list_sessions(self, limit: int = 20, offset: int = 0) -> List[ConversationSession]:
        """列出会话列表"""
        try:
            rows = await self._execute_query("""
                SELECT * FROM conversation_sessions 
                ORDER BY updated_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset), fetch=True)
            
            sessions = []
            for row in rows:
                row_data = dict(row)
                sessions.append(ConversationSession.from_dict(row_data))
            
            return sessions
            
        except Exception as e:
            logger.error(f"获取会话列表失败: {e}")
            return []
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话和相关数据"""
        try:
            # 删除消息
            await self._execute_query("DELETE FROM conversation_messages WHERE session_id = ?", (session_id,))
            
            # 删除总结
            await self._execute_query("DELETE FROM conversation_summaries WHERE session_id = ?", (session_id,))
            
            # 删除会话
            await self._execute_query("DELETE FROM conversation_sessions WHERE session_id = ?", (session_id,))
            
            logger.info(f"会话已删除: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False
    
    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """清理旧会话（保留最近N天）"""
        try:
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 获取要删除的会话ID
            rows = await self._execute_query("""
                SELECT session_id FROM conversation_sessions 
                WHERE updated_at < ?
            """, (cutoff_date,), fetch=True)
            
            deleted_count = 0
            for row in rows:
                session_id = row['session_id']
                if await self.delete_session(session_id):
                    deleted_count += 1
            
            logger.info(f"清理了 {deleted_count} 个旧会话")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧会话失败: {e}")
            return 0


# 全局存储实例
storage = SQLiteConversationStorage("data/conversations.db")
