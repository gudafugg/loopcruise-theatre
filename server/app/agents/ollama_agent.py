# -*- coding: utf-8 -*-
"""
基于Ollama的本地AI Agent实现
"""
import asyncio
import json
import re
from typing import AsyncGenerator, Dict, List, Optional
import aiohttp
from loguru import logger

from .base_agent import BaseAgent, ScriptContext, UserInput, AgentResponse


class OllamaAgent(BaseAgent):
    """基于Ollama的本地AI Agent"""
    
    def __init__(self, 
                 model_name: str = "qwen2.5:7b", 
                 ollama_url: str = "http://localhost:11434"):
        super().__init__("OllamaAgent")
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.session = None
        
    async def _get_session(self):
        """获取aiohttp会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """关闭会话"""
        if self.session:
            await self.session.close()
    
    async def _call_ollama(self, prompt: str, stream: bool = False) -> str:
        """调用Ollama API"""
        session = await self._get_session()
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        try:
            async with session.post(f"{self.ollama_url}/api/generate", 
                                  json=payload) as response:
                if stream:
                    return response  # 返回response对象用于流式处理
                else:
                    result = await response.json()
                    return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama API调用失败: {e}")
            return "抱歉，AI服务暂时不可用。"
    
    async def load_script(self, script_text: str) -> bool:
        """加载并解析剧本"""
        try:
            # 使用AI解析剧本结构
            parse_prompt = f"""
请分析以下剧本，提取关键信息并以JSON格式返回：

剧本内容：
{script_text}

请返回以下JSON格式：
{{
    "title": "剧本标题",
    "characters": [
        {{"name": "角色名", "description": "角色描述"}},
        ...
    ],
    "setting": "场景设定",
    "plot_summary": "剧情概要"
}}

只返回JSON，不要其他内容：
"""
            
            response = await self._call_ollama(parse_prompt)
            
            # 尝试解析JSON响应
            try:
                # 提取JSON部分
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    
                    self.script_context = ScriptContext(
                        title=parsed_data.get("title", "未命名剧本"),
                        characters=parsed_data.get("characters", []),
                        setting=parsed_data.get("setting", ""),
                        plot_summary=parsed_data.get("plot_summary", ""),
                        full_script=script_text
                    )
                    
                    logger.info(f"成功加载剧本: {self.script_context.title}")
                    return True
                else:
                    raise ValueError("无法解析JSON响应")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON解析失败，使用默认结构: {e}")
                # 如果解析失败，使用基本结构
                self.script_context = ScriptContext(
                    title="导入的剧本",
                    characters=[{"name": "AI", "description": "智能助手"}],
                    setting="互动剧场",
                    plot_summary="基于用户输入的互动剧情",
                    full_script=script_text
                )
                return True
                
        except Exception as e:
            logger.error(f"加载剧本失败: {e}")
            return False
    
    async def generate_response(self, user_input: UserInput) -> AgentResponse:
        """生成单次响应"""
        if not self.script_context:
            return AgentResponse(
                speaker_id="system",
                text="请先加载剧本。",
                confidence=0.0
            )
        
        # 构建提示词
        prompt = self._build_prompt(user_input)
        
        # 调用Ollama生成响应
        ai_response = await self._call_ollama(prompt)
        
        # 解析AI响应
        return self._parse_ai_response(ai_response)
    
    async def stream_response(self, user_input: UserInput) -> AsyncGenerator[str, None]:
        """流式生成响应"""
        if not self.script_context:
            yield "请先加载剧本。"
            return
        
        prompt = self._build_prompt(user_input)
        
        try:
            session = await self._get_session()
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9
                }
            }
            
            async with session.post(f"{self.ollama_url}/api/generate", 
                                  json=payload) as response:
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                yield data['response']
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"流式响应生成失败: {e}")
            yield "抱歉，生成响应时出现问题。"
    
    def _build_prompt(self, user_input: UserInput) -> str:
        """构建提示词"""
        context = self.script_context
        
        prompt = f"""你是一个专业的互动剧本AI助手。

# 剧本背景
标题：{context.title}
设定：{context.setting}
剧情概要：{context.plot_summary}

# 角色信息
{chr(10).join([f"- {char['name']}: {char.get('description', '暂无描述')}" for char in context.characters])}

# 原始剧本参考
{context.full_script[:1000]}...

# 任务
根据用户输入，生成符合剧本风格和世界观的续写内容。要求：
1. 保持角色性格一致
2. 符合剧本的整体氛围和设定
3. 自然流畅地续写剧情
4. 可以引入新的情节转折

# 用户输入
{user_input.text}

# 回复要求
请以角色对话或旁白的形式回复，格式如下：
[角色名]："对话内容"
或
（旁白描述）

开始创作："""
        
        return prompt
    
    def _parse_ai_response(self, response: str) -> AgentResponse:
        """解析AI响应"""
        # 尝试提取角色和对话
        speaker_match = re.match(r'\[([^\]]+)\]：?"([^"]+)"', response)
        narrator_match = re.match(r'（([^）]+)）', response)
        
        if speaker_match:
            speaker = speaker_match.group(1)
            text = speaker_match.group(2)
            return AgentResponse(
                speaker_id=speaker.lower().replace(" ", "_"),
                text=text,
                confidence=0.9
            )
        elif narrator_match:
            return AgentResponse(
                speaker_id="narrator",
                text=narrator_match.group(1),
                confidence=0.8
            )
        else:
            # 如果无法解析格式，直接返回原文
            return AgentResponse(
                speaker_id="ai",
                text=response.strip(),
                confidence=0.7
            )


# 使用示例和测试代码
async def test_ollama_agent():
    """测试函数"""
    agent = OllamaAgent()
    
    # 测试剧本
    test_script = """
    标题：海上奇遇
    
    丁奇：船长，勇敢而神秘
    小艾：新手船员，充满好奇心
    
    场景：一艘古老的帆船在暴风雨后的海面上
    
    [丁奇]："风暴已经过去了，但我们偏离了航线。"
    [小艾]："船长，那边有个小岛！"
    （海鸥在空中盘旋，发出尖锐的叫声）
    """
    
    # 加载剧本
    success = await agent.load_script(test_script)
    if success:
        print("✓ 剧本加载成功")
        print(f"剧本标题：{agent.script_context.title}")
        
        # 测试对话生成
        user_input = UserInput(
            text="我想知道那个小岛上有什么",
            session_id="test_session"
        )
        
        response = await agent.generate_response(user_input)
        print(f"AI响应：[{response.speaker_id}] {response.text}")
    
    await agent.close()


if __name__ == "__main__":
    asyncio.run(test_ollama_agent())
