# -*- coding: utf-8 -*-
"""
数据库模型定义 - 对话存储和会话管理
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json


class MessageType(Enum):
    """消息类型枚举"""
    USER = "user"           # 用户输入
    ASSISTANT = "assistant" # AI助手回复
    SYSTEM = "system"       # 系统消息
    NARRATOR = "narrator"   # 旁白


class MessageRole(Enum):
    """消息角色枚举"""
    PLAYER = "player"       # 玩家
    NPC = "npc"            # NPC角色
    DM = "dm"              # 剧情管理员
    SYSTEM = "system"       # 系统


@dataclass
class ConversationMessage:
    """对话消息数据模型"""
    id: Optional[int] = None
    session_id: str = ""
    message_type: MessageType = MessageType.USER
    role: MessageRole = MessageRole.PLAYER
    speaker_name: str = ""
    content: str = ""
    metadata: Dict[str, Any] = None  # 存储额外信息（情感、置信度等）
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['role'] = self.role.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['metadata'] = json.dumps(self.metadata) if self.metadata else '{}'
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """从字典创建实例"""
        # 处理枚举字段
        if 'message_type' in data:
            data['message_type'] = MessageType(data['message_type'])
        if 'role' in data:
            data['role'] = MessageRole(data['role'])
        
        # 处理时间字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # 处理JSON字段
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata']) if data['metadata'] else {}
        
        return cls(**data)


@dataclass
class ConversationSession:
    """对话会话数据模型"""
    session_id: str
    script_title: str = ""
    script_content: str = ""
    agent_model: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        data['metadata'] = json.dumps(self.metadata) if self.metadata else '{}'
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSession':
        """从字典创建实例"""
        # 处理时间字段
        for field in ['created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        
        # 处理JSON字段
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata']) if data['metadata'] else {}
        
        return cls(**data)


@dataclass
class ConversationSummary:
    """对话总结数据模型（用于长期记忆压缩）"""
    id: Optional[int] = None
    session_id: str = ""
    summary_content: str = ""
    message_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        for field in ['start_time', 'end_time', 'created_at']:
            if data[field]:
                data[field] = data[field].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSummary':
        """从字典创建实例"""
        # 处理时间字段
        for field in ['start_time', 'end_time', 'created_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)
