# -*- coding: utf-8 -*-
"""
带记忆功能的AI Agent实现
支持对话历史存储和上下文理解
"""

import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, List, Optional
from loguru import logger

from .ollama_agent import OllamaAgent  
from .base_agent import UserInput, AgentResponse
from ..database.models import ConversationMessage, ConversationSession, MessageType, MessageRole
from ..database.sqlite_storage import storage


class MemoryEnhancedAgent(OllamaAgent):
    """增强的AI Agent - 支持对话记忆"""
    
    def __init__(self, 
                 model_name: str = "qwen2.5:7b", 
                 ollama_url: str = "http://localhost:11434",
                 max_history_messages: int = 10):
        super().__init__(model_name, ollama_url)
        self.max_history_messages = max_history_messages
        self.current_session: Optional[ConversationSession] = None
        
    async def initialize_session(self, session_id: str) -> bool:
        """初始化会话（从数据库加载或创建新会话）"""
        try:
            # 确保数据库已初始化
            await storage.initialize()
            
            # 尝试从数据库加载现有会话
            session = await storage.get_session(session_id)
            
            if session:
                logger.info(f"从数据库加载会话: {session_id}")
                self.current_session = session
                
                # 如果会话中有剧本，重新加载
                if session.script_content:
                    await self.load_script(session.script_content)
                
                return True
            else:
                # 创建新会话
                logger.info(f"创建新会话: {session_id}")
                self.current_session = ConversationSession(
                    session_id=session_id,
                    agent_model=self.model_name
                )
                await storage.save_session(self.current_session)
                return True
                
        except Exception as e:
            logger.error(f"会话初始化失败: {e}")
            return False
    
    async def load_script(self, script_text: str) -> bool:
        """加载剧本并保存到数据库"""
        # 调用父类方法解析剧本
        success = await super().load_script(script_text)
        
        if success and self.current_session and self.script_context:
            # 更新会话信息
            self.current_session.script_title = self.script_context.title
            self.current_session.script_content = script_text
            self.current_session.updated_at = datetime.now()
            
            # 保存到数据库
            await storage.save_session(self.current_session)
            
            # 记录系统消息
            await self._save_system_message(f"剧本已加载: {self.script_context.title}")
            
        return success
    
    async def generate_response_with_memory(self, user_input: UserInput) -> AgentResponse:
        """生成带记忆的响应"""
        if not self.current_session:
            await self.initialize_session(user_input.session_id)
        
        # 保存用户消息到数据库
        user_message = ConversationMessage(
            session_id=user_input.session_id,
            message_type=MessageType.USER,
            role=MessageRole.PLAYER,
            speaker_name="玩家",
            content=user_input.text
        )
        await storage.save_message(user_message)
        
        # 获取对话历史作为上下文
        conversation_history = await storage.get_recent_context(
            user_input.session_id, 
            self.max_history_messages
        )
        
        # 构建包含历史的提示词
        enhanced_prompt = await self._build_memory_prompt(user_input, conversation_history)
        
        # 调用AI生成响应
        ai_response = await self._call_ollama(enhanced_prompt)
        parsed_response = self._parse_ai_response(ai_response)
        
        # 保存AI响应到数据库
        ai_message = ConversationMessage(
            session_id=user_input.session_id,
            message_type=MessageType.ASSISTANT,
            role=MessageRole.NPC if parsed_response.speaker_id != "ai" else MessageRole.DM,
            speaker_name=parsed_response.speaker_id,
            content=parsed_response.text,
            metadata={
                'confidence': parsed_response.confidence,
                'emotion': parsed_response.emotion,
                'model': self.model_name
            }
        )
        await storage.save_message(ai_message)
        
        # 更新会话时间戳
        if self.current_session:
            self.current_session.updated_at = datetime.now()
            await storage.save_session(self.current_session)
        
        return parsed_response
    
    async def stream_response_with_memory(self, user_input: UserInput) -> AsyncGenerator[str, None]:
        """流式生成带记忆的响应"""
        if not self.current_session:
            await self.initialize_session(user_input.session_id)
        
        # 保存用户消息
        user_message = ConversationMessage(
            session_id=user_input.session_id,
            message_type=MessageType.USER,
            role=MessageRole.PLAYER,
            speaker_name="玩家",
            content=user_input.text
        )
        await storage.save_message(user_message)
        
        # 获取对话历史
        conversation_history = await storage.get_recent_context(
            user_input.session_id,
            self.max_history_messages
        )
        
        # 构建提示词
        enhanced_prompt = await self._build_memory_prompt(user_input, conversation_history)
        
        # 流式生成并收集完整响应
        full_response = ""
        try:
            async for chunk in self.stream_response(UserInput(
                text=enhanced_prompt,
                session_id=user_input.session_id
            )):
                full_response += chunk
                yield chunk
        except Exception as e:
            logger.error(f"流式生成失败: {e}")
            yield "抱歉，AI服务出现问题。"
            return
        
        # 保存完整的AI响应
        if full_response.strip():
            parsed_response = self._parse_ai_response(full_response)
            ai_message = ConversationMessage(
                session_id=user_input.session_id,
                message_type=MessageType.ASSISTANT,
                role=MessageRole.NPC if parsed_response.speaker_id != "ai" else MessageRole.DM,
                speaker_name=parsed_response.speaker_id,
                content=parsed_response.text,
                metadata={
                    'confidence': parsed_response.confidence,
                    'model': self.model_name,
                    'stream_generated': True
                }
            )
            await storage.save_message(ai_message)
            
            # 更新会话
            if self.current_session:
                self.current_session.updated_at = datetime.now()
                await storage.save_session(self.current_session)
    
    async def _build_memory_prompt(self, user_input: UserInput, history: List[ConversationMessage]) -> str:
        """构建包含记忆的提示词"""
        context = self.script_context
        if not context:
            return user_input.text
        
        # 构建对话历史字符串
        history_text = ""
        if history:
            history_text = "\n# 对话历史\n"
            for msg in history[-8:]:  # 只取最近8条
                role_name = "玩家" if msg.message_type == MessageType.USER else msg.speaker_name
                history_text += f"[{role_name}]: {msg.content}\n"
            history_text += "\n"
        
        prompt = f"""你是一个专业的互动剧本AI助手，具有完整的对话记忆能力。

# 剧本背景
标题：{context.title}
设定：{context.setting}
剧情概要：{context.plot_summary}

# 角色信息
{chr(10).join([f"- {char['name']}: {char.get('description', '暂无描述')}" for char in context.characters])}

{history_text}# 当前用户输入
{user_input.text}

# 任务要求
1. 根据对话历史和剧本背景，生成连贯的剧情续写
2. 保持角色性格和剧情逻辑的一致性
3. 自然地融合历史对话中的情节发展
4. 可以引入新的情节转折，但要符合整体世界观

# 回复格式
请以角色对话或旁白的形式回复：
[角色名]："对话内容"
或
（旁白描述）

开始创作："""
        
        return prompt
    
    async def _save_system_message(self, content: str) -> None:
        """保存系统消息"""
        if self.current_session:
            system_message = ConversationMessage(
                session_id=self.current_session.session_id,
                message_type=MessageType.SYSTEM,
                role=MessageRole.SYSTEM,
                speaker_name="系统",
                content=content
            )
            await storage.save_message(system_message)
    
    async def get_conversation_summary(self) -> Optional[str]:
        """获取对话摘要"""
        if not self.current_session:
            return None
        
        try:
            stats = await storage.get_conversation_stats(self.current_session.session_id)
            history = await storage.get_conversation_history(self.current_session.session_id, limit=20)
            
            if not history:
                return "暂无对话记录"
            
            # 构建摘要
            summary_parts = []
            summary_parts.append(f"对话统计: 共 {stats.get('total_messages', 0)} 条消息")
            
            if self.script_context:
                summary_parts.append(f"当前剧本: {self.script_context.title}")
            
            # 提取关键对话
            key_messages = [msg for msg in history if len(msg.content) > 10][-5:]
            if key_messages:
                summary_parts.append("最近关键对话:")
                for msg in key_messages:
                    role = "玩家" if msg.message_type == MessageType.USER else msg.speaker_name
                    content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                    summary_parts.append(f"  [{role}]: {content}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"生成对话摘要失败: {e}")
            return None
    
    async def export_conversation(self) -> Optional[dict]:
        """导出完整对话记录"""
        if not self.current_session:
            return None
        
        try:
            session_data = self.current_session.to_dict()
            messages = await storage.get_conversation_history(
                self.current_session.session_id,
                limit=1000
            )
            
            return {
                'session': session_data,
                'messages': [msg.to_dict() for msg in messages],
                'export_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"导出对话失败: {e}")
            return None
