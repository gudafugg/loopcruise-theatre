#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
带记忆功能的AI Agent测试脚本

测试功能：
1. 对话存储到数据库
2. 上下文记忆和理解
3. 对话历史查询
4. 会话管理

使用方法：
1. 确保Ollama服务运行
2. 运行: python test_memory_agent.py
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from typing import List, Dict


class MemoryAgentTester:
    """带记忆Agent测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        
    async def test_complete_memory_workflow(self):
        """测试完整的记忆工作流程"""
        print("🧠 开始AI Agent记忆功能测试...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # 1. 创建会话并加载剧本
                await self._test_create_session_and_load_script(session)
                
                # 2. 测试多轮对话记忆
                await self._test_multi_turn_conversation(session)
                
                # 3. 测试对话历史查询
                await self._test_conversation_history(session)
                
                # 4. 测试对话统计和摘要
                await self._test_conversation_stats(session)
                
                # 5. 测试搜索功能
                await self._test_conversation_search(session)
                
                # 6. 测试数据导出
                await self._test_conversation_export(session)
                
                print("✅ 所有记忆功能测试通过！")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                
            finally:
                # 清理（可选）
                await self._cleanup_test_data(session)
    
    async def _test_create_session_and_load_script(self, session: aiohttp.ClientSession):
        """测试创建会话和加载剧本"""
        print("\n📚 测试1: 创建会话并加载剧本")
        
        # 创建SSE会话
        async with session.post(f"{self.base_url}/api/v1/stream/start", 
                               json={}) as response:
            if response.status == 200:
                data = await response.json()
                self.session_id = data["session_id"]
                print(f"✓ 会话创建成功: {self.session_id}")
        
        # 加载测试剧本
        test_script = """
        标题：时空旅者的咖啡馆
        
        主要角色：
        - 艾莉丝：神秘的咖啡馆老板，掌握时空穿越的秘密
        - 教授：来自未来的物理学家，正在寻找回到自己时代的方法
        - 玛丽：年轻的作家，意外发现了这个奇妙的地方
        
        场景设定：
        一个隐藏在城市角落的神秘咖啡馆，每一杯咖啡都能带人穿越到不同的时空。
        咖啡馆外表看起来很普通，但内部充满了各个时代的物品和记忆。
        
        剧情概要：
        不同时代的人们因为各种原因来到这个咖啡馆，他们在这里相遇、交流，
        分享着各自的故事和时代的秘密。每个人都在寻找着什么，
        而咖啡馆老板艾莉丝似乎知道所有的答案。
        
        开场：
        [艾莉丝]："欢迎来到时光咖啡馆。您想要什么样的咖啡？每一种都有着不同的故事。"
        [教授]："我需要找到回到2150年的方法，听说这里能帮到我。"
        （咖啡馆里弥漫着淡淡的香气，墙上挂着各个时代的钟表，它们的指针都指向不同的时间）
        """
        
        payload = {
            "session_id": self.session_id,
            "script_text": test_script
        }
        
        async with session.post(f"{self.base_url}/api/v1/agent/load_script", 
                               json=payload) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ 剧本加载成功: {data.get('script_title', '未命名')}")
            else:
                error_text = await response.text()
                raise Exception(f"剧本加载失败: {response.status} - {error_text}")
    
    async def _test_multi_turn_conversation(self, session: aiohttp.ClientSession):
        """测试多轮对话记忆"""
        print("\n💬 测试2: 多轮对话记忆")
        
        conversation_turns = [
            "我刚走进这个咖啡馆，感觉很神奇。能告诉我这里的故事吗？",
            "我注意到教授提到2150年，他是从未来来的吗？",
            "艾莉丝看起来很神秘，她是这里的主人吗？",
            "我想尝试一杯能带我看到过去的咖啡",
            "刚才我们谈到的时空穿越，这真的可能吗？"
        ]
        
        for i, message in enumerate(conversation_turns, 1):
            print(f"\n👤 轮次{i}: {message}")
            
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
                    
                    # 等待一下，模拟真实对话
                    await asyncio.sleep(1)
                else:
                    error_text = await response.text()
                    print(f"❌ 对话失败: {response.status} - {error_text}")
    
    async def _test_conversation_history(self, session: aiohttp.ClientSession):
        """测试对话历史查询"""
        print("\n📜 测试3: 对话历史查询")
        
        # 获取对话历史
        async with session.get(f"{self.base_url}/api/v1/conversation/history/{self.session_id}?limit=10") as response:
            if response.status == 200:
                data = await response.json()
                messages = data["messages"]
                print(f"✓ 获取到 {len(messages)} 条历史消息")
                print(f"✓ 总消息数: {data['total_count']}")
                
                # 显示最近几条消息
                print("\n最近的对话记录:")
                for msg in messages[-3:]:
                    msg_type = "👤用户" if msg["message_type"] == "user" else f"🤖{msg['speaker_name']}"
                    content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                    print(f"  {msg_type}: {content}")
            else:
                print(f"❌ 获取历史失败: {response.status}")
    
    async def _test_conversation_stats(self, session: aiohttp.ClientSession):
        """测试对话统计和摘要"""
        print("\n📊 测试4: 对话统计和摘要")
        
        # 获取统计信息
        async with session.get(f"{self.base_url}/api/v1/conversation/stats/{self.session_id}") as response:
            if response.status == 200:
                data = await response.json()
                stats = data["stats"]
                print(f"✓ 总消息数: {stats.get('total_messages', 0)}")
                print(f"✓ 用户消息: {stats.get('user_messages', 0)}")
                print(f"✓ AI消息: {stats.get('ai_messages', 0)}")
            else:
                print(f"❌ 获取统计失败: {response.status}")
        
        # 获取对话摘要
        async with session.get(f"{self.base_url}/api/v1/conversation/summary/{self.session_id}") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ 剧本标题: {data['session_info'].get('script_title', '未知')}")
                print("✓ 最近亮点:")
                for highlight in data.get("recent_highlights", []):
                    print(f"  [{highlight['speaker']}]: {highlight['content']}")
            else:
                print(f"❌ 获取摘要失败: {response.status}")
    
    async def _test_conversation_search(self, session: aiohttp.ClientSession):
        """测试对话搜索"""
        print("\n🔍 测试5: 对话搜索")
        
        search_terms = ["咖啡馆", "时空", "艾莉丝"]
        
        for term in search_terms:
            async with session.get(f"{self.base_url}/api/v1/conversation/search/{self.session_id}?query={term}&limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    matches = data["matches"]
                    print(f"✓ 搜索 '{term}': 找到 {len(matches)} 条匹配")
                    
                    for match in matches[:2]:  # 只显示前2条
                        content = match["content"][:30] + "..." if len(match["content"]) > 30 else match["content"]
                        print(f"  - {content}")
                else:
                    print(f"❌ 搜索 '{term}' 失败: {response.status}")
    
    async def _test_conversation_export(self, session: aiohttp.ClientSession):
        """测试对话导出"""
        print("\n📤 测试6: 对话导出")
        
        async with session.get(f"{self.base_url}/api/v1/conversation/export/{self.session_id}") as response:
            if response.status == 200:
                data = await response.json()
                export_info = data["export_info"]
                print(f"✓ 导出成功: {export_info['total_messages']} 条消息")
                print(f"✓ 导出时间: {export_info['export_time']}")
                
                # 保存到文件（可选）
                filename = f"conversation_export_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"✓ 已保存到文件: {filename}")
                except Exception as e:
                    print(f"⚠️ 保存文件失败: {e}")
            else:
                print(f"❌ 导出失败: {response.status}")
    
    async def _cleanup_test_data(self, session: aiohttp.ClientSession):
        """清理测试数据"""
        print(f"\n🧹 清理测试数据: {self.session_id}")
        
        response = input("是否删除测试会话数据？(y/N): ")
        if response.lower() == 'y':
            async with session.delete(f"{self.base_url}/api/v1/conversation/session/{self.session_id}") as resp:
                if resp.status == 200:
                    print("✓ 测试数据已清理")
                else:
                    print(f"⚠️ 清理失败: {resp.status}")
        else:
            print("ℹ️ 保留测试数据，可通过API手动管理")


async def check_memory_services():
    """检查记忆功能相关服务"""
    print("🔍 检查记忆功能服务状态...")
    
    # 检查FastAPI服务
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/docs") as response:
                if response.status == 200:
                    print("✓ FastAPI服务正常")
                else:
                    print(f"⚠️ FastAPI响应异常: {response.status}")
    except Exception as e:
        print(f"❌ FastAPI服务异常: {e}")
        return False
    
    # 检查Ollama服务
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    print("✓ Ollama服务正常")
                else:
                    print(f"⚠️ Ollama响应异常: {response.status}")
    except Exception as e:
        print(f"❌ Ollama服务异常: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🧠 LoopcruiseTheatre AI Agent 记忆功能测试")
    print("=" * 60)
    
    async def main():
        # 检查服务
        if not await check_memory_services():
            print("\n⚠️ 请确保所需服务正在运行:")
            print("  - FastAPI: python start_server.py")  
            print("  - Ollama: ollama serve")
            return
        
        # 运行测试
        tester = MemoryAgentTester()
        await tester.test_complete_memory_workflow()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试已中断")
    except Exception as e:
        print(f"\n\n💥 测试出现异常: {e}")
