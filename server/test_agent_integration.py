#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent集成测试脚本

测试流程：
1. 启动SSE会话
2. 加载剧本
3. 进行对话
4. 验证流式响应

使用方法：
1. 确保Ollama服务运行在localhost:11434
2. 确保FastAPI服务运行在localhost:8000
3. 运行: python test_agent_integration.py
"""

import asyncio
import json
import aiohttp
from typing import AsyncGenerator


class AgentIntegrationTester:
    """Agent集成测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        
    async def test_complete_workflow(self):
        """测试完整的工作流程"""
        print("🚀 开始AI Agent集成测试...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # 1. 创建SSE会话
                await self._test_create_session(session)
                
                # 2. 加载测试剧本
                await self._test_load_script(session)
                
                # 3. 测试对话
                await self._test_chat(session)
                
                # 4. 测试流式对话
                await self._test_stream_chat(session)
                
                # 5. 检查Agent状态
                await self._test_agent_status(session)
                
                print("✅ 所有测试通过！")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                
            finally:
                # 清理会话
                if self.session_id:
                    await self._cleanup_session(session)
    
    async def _test_create_session(self, session: aiohttp.ClientSession):
        """测试创建SSE会话"""
        print("\n📡 测试1: 创建SSE会话")
        
        async with session.post(f"{self.base_url}/api/v1/stream/start", 
                               json={"hello": True}) as response:
            if response.status == 200:
                data = await response.json()
                self.session_id = data["session_id"]
                print(f"✓ 会话创建成功: {self.session_id}")
            else:
                raise Exception(f"会话创建失败: {response.status}")
    
    async def _test_load_script(self, session: aiohttp.ClientSession):
        """测试加载剧本"""
        print("\n📚 测试2: 加载剧本")
        
        test_script = """
        标题：海上奇遇记
        
        主要角色：
        - 丁奇：经验丰富的老船长，性格沉稳但内心充满冒险精神
        - 小艾：年轻的船员，好奇心旺盛，对未知世界充满向往
        - 神秘商人：在小岛上遇到的奇怪人物
        
        场景设定：
        大航海时代，一艘商船在暴风雨后偏离航线，发现了一个神秘的小岛。
        岛上有着古老的遗迹和未知的秘密。
        
        剧情概要：
        船员们在神秘小岛上探险，遇到了奇怪的现象和神秘人物，
        需要解开岛屿的谜团才能找到回家的路。
        
        开场剧本：
        [丁奇]："风暴终于停了...看，那边有个小岛！"
        [小艾]："船长，我们要去看看吗？岛上好像有烟雾。"
        （海浪轻拍着船侧，远处的小岛若隐若现）
        [丁奇]："准备小船，我们去岛上看看。也许能找到淡水和食物。"
        """
        
        payload = {
            "session_id": self.session_id,
            "script_text": test_script,
            "model_name": "qwen2.5:7b"
        }
        
        async with session.post(f"{self.base_url}/api/v1/agent/load_script", 
                               json=payload) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ 剧本加载成功: {data['script_title']}")
                
                # 等待一下让AI处理完毕
                await asyncio.sleep(2)
            else:
                error_text = await response.text()
                raise Exception(f"剧本加载失败: {response.status} - {error_text}")
    
    async def _test_chat(self, session: aiohttp.ClientSession):
        """测试普通对话"""
        print("\n💬 测试3: 普通对话")
        
        test_messages = [
            "我们现在登上小岛了，四周看起来很神秘",
            "岛上那个冒烟的地方是什么？",
            "我听到了奇怪的声音，像是有人在说话"
        ]
        
        for message in test_messages:
            print(f"👤 用户: {message}")
            
            payload = {
                "session_id": self.session_id,
                "message": message,
                "stream": False
            }
            
            async with session.post(f"{self.base_url}/api/v1/agent/chat", 
                                   json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["success"] and "response" in data:
                        resp = data["response"]
                        print(f"🤖 [{resp['speaker_id']}]: {resp['text']}")
                else:
                    error_text = await response.text()
                    print(f"❌ 对话失败: {response.status} - {error_text}")
                
                await asyncio.sleep(1)
    
    async def _test_stream_chat(self, session: aiohttp.ClientSession):
        """测试流式对话"""
        print("\n🌊 测试4: 流式对话")
        
        message = "突然间，我们发现了一个古老的石碑，上面刻着神秘的符号，你能帮我们解读吗？"
        print(f"👤 用户: {message}")
        
        payload = {
            "session_id": self.session_id,
            "message": message,
            "stream": True
        }
        
        async with session.post(f"{self.base_url}/api/v1/agent/chat", 
                               json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if data["success"]:
                    print("🤖 AI开始流式回复...")
                    
                    # 监听SSE流
                    await self._listen_sse_stream()
                else:
                    print(f"❌ 流式对话启动失败: {data}")
            else:
                error_text = await response.text()
                print(f"❌ 流式对话失败: {response.status} - {error_text}")
    
    async def _listen_sse_stream(self):
        """监听SSE流"""
        sse_url = f"{self.base_url}/api/v1/stream/sse?session_id={self.session_id}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(sse_url) as response:
                    if response.status == 200:
                        buffer = ""
                        timeout_count = 0
                        max_timeout = 30  # 30秒超时
                        
                        async for line_bytes in response.content:
                            line = line_bytes.decode('utf-8').strip()
                            
                            if line.startswith('data: '):
                                try:
                                    event_data = json.loads(line[6:])
                                    await self._handle_sse_event(event_data)
                                    timeout_count = 0  # 重置超时计数
                                except json.JSONDecodeError:
                                    continue
                            
                            # 简单的超时机制
                            timeout_count += 1
                            if timeout_count > max_timeout:
                                print("⏰ SSE监听超时，结束监听")
                                break
                                
                            await asyncio.sleep(0.1)
                    else:
                        print(f"❌ SSE连接失败: {response.status}")
                        
            except Exception as e:
                print(f"❌ SSE监听出错: {e}")
    
    async def _handle_sse_event(self, event_data):
        """处理SSE事件"""
        if event_data.get("type") == "ai_stream":
            chunk = event_data.get("chunk", "")
            if chunk:
                print(f"🤖 [流式]: {chunk}", end="", flush=True)
        elif event_data.get("type") == "npc":
            print(f"\n🎭 [{event_data['speaker_id']}]: {event_data['text']}")
        elif event_data.get("type") == "agent_status":
            print(f"📊 状态: {event_data['message']}")
        elif event_data.get("type") == "error":
            print(f"❌ 错误: {event_data['message']}")
    
    async def _test_agent_status(self, session: aiohttp.ClientSession):
        """测试Agent状态查询"""
        print("\n📊 测试5: 查询Agent状态")
        
        async with session.get(f"{self.base_url}/api/v1/agent/status/{self.session_id}") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ Agent状态: {data['status']}")
                print(f"✓ 剧本已加载: {data['script_loaded']}")
                if data['script_title']:
                    print(f"✓ 剧本标题: {data['script_title']}")
            else:
                error_text = await response.text()
                print(f"❌ 状态查询失败: {response.status} - {error_text}")
    
    async def _cleanup_session(self, session: aiohttp.ClientSession):
        """清理会话"""
        print(f"\n🧹 清理会话: {self.session_id}")
        
        async with session.delete(f"{self.base_url}/api/v1/agent/session/{self.session_id}") as response:
            if response.status == 200:
                print("✓ 会话清理完成")
            else:
                print(f"⚠️ 会话清理失败: {response.status}")


async def check_services():
    """检查服务状态"""
    print("🔍 检查服务状态...")
    
    # 检查FastAPI服务
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000") as response:
                print("✓ FastAPI服务正常")
    except Exception as e:
        print(f"❌ FastAPI服务异常: {e}")
        print("请确保FastAPI服务在localhost:8000运行")
        return False
    
    # 检查Ollama服务
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    print(f"✓ Ollama服务正常，可用模型: {models}")
                    
                    if "qwen2.5:7b" not in models:
                        print("⚠️ 建议安装qwen2.5:7b模型: ollama pull qwen2.5:7b")
                else:
                    print("❌ Ollama服务响应异常")
                    return False
    except Exception as e:
        print(f"❌ Ollama服务异常: {e}")
        print("请确保Ollama服务在localhost:11434运行")
        return False
    
    return True


if __name__ == "__main__":
    print("🎭 LoopcruiseTheatre AI Agent集成测试")
    print("=" * 50)
    
    async def main():
        # 检查服务
        if not await check_services():
            return
        
        # 运行测试
        tester = AgentIntegrationTester()
        await tester.test_complete_workflow()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试已中断")
    except Exception as e:
        print(f"\n\n💥 测试出现异常: {e}")
