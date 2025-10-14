# -*- coding: utf-8 -*-
"""
基础Agent接口定义
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass


@dataclass
class ScriptContext:
    """剧本上下文"""
    title: str
    characters: List[Dict[str, str]]  # [{"name": "丁奇", "description": "..."}, ...]
    setting: str  # 场景设定
    plot_summary: str  # 剧情概要
    full_script: str  # 完整剧本文本


@dataclass
class UserInput:
    """用户输入"""
    text: str
    session_id: str
    context: Optional[str] = None  # 当前对话上下文


@dataclass
class AgentResponse:
    """Agent响应"""
    speaker_id: str
    text: str
    emotion: Optional[str] = None
    action: Optional[str] = None
    confidence: float = 1.0


class BaseAgent(ABC):
    """AI Agent基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.script_context: Optional[ScriptContext] = None
    
    @abstractmethod
    async def load_script(self, script_text: str) -> bool:
        """加载剧本并解析上下文"""
        pass
    
    @abstractmethod
    async def generate_response(self, user_input: UserInput) -> AgentResponse:
        """生成剧情响应"""
        pass
    
    @abstractmethod
    async def stream_response(self, user_input: UserInput) -> AsyncGenerator[str, None]:
        """流式生成响应"""
        pass
