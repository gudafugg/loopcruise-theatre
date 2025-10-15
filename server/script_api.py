#!/usr/bin/env python3
"""
《迷失》剧本对话API - 供AI Agent使用
提供简单易用的接口访问剧本对话数据
"""
from fastapi import FastAPI, HTTPException, Query
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional

app = FastAPI(
    title="《迷失》剧本对话API", 
    version="1.0.0",
    description="专为AI Agent设计的《迷失》剧本对话数据访问接口"
)

DB_PATH = Path("data/conversations.db")

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
async def root():
    """API根路径"""
    return {
        "api": "《迷失》剧本对话API",
        "version": "1.0.0", 
        "description": "为AI Agent提供《迷失》剧本对话数据访问",
        "script_info": {
            "title": "《迷失》",
            "description": "一个关于多重人格少年被绑架后的心理悬疑剧本",
            "characters": ["周二", "汤尚", "绑架犯", "妈妈", "小白"]
        },
        "endpoints": {
            "获取所有对话": "/dialogues",
            "按角色搜索": "/speaker/{speaker_name}",
            "按场景搜索": "/scene/{scene_name}",
            "搜索对话内容": "/search?q={query}",
            "获取角色列表": "/speakers",
            "获取场景列表": "/scenes",
            "统计信息": "/stats"
        }
    }

@app.get("/dialogues")
async def get_all_dialogues(limit: Optional[int] = Query(None, description="限制返回数量")):
    """
    获取《迷失》剧本中的所有对话
    
    - **limit**: 限制返回的对话数量
    """
    try:
        conn = get_db_connection()
        
        if limit:
            cursor = conn.execute("""
                SELECT * FROM conversation_messages 
                WHERE role = 'dialogue'
                ORDER BY timestamp 
                LIMIT ?
            """, (limit,))
        else:
            cursor = conn.execute("""
                SELECT * FROM conversation_messages 
                WHERE role = 'dialogue'
                ORDER BY timestamp
            """)
        
        messages = cursor.fetchall()
        conn.close()
        
        dialogues = []
        for msg in messages:
            try:
                metadata = json.loads(msg["metadata"]) if msg["metadata"] else {}
                # 提取纯对话内容（去掉[角色说]: 前缀）
                content = msg["content"]
                if "]: " in content:
                    content = content.split("]: ", 1)[1]
                
                dialogue = {
                    "id": msg["id"],
                    "speaker": metadata.get("speaker", "未知"),
                    "content": content,
                    "scene": metadata.get("scene", ""),
                    "sequence": metadata.get("sequence", 0),
                    "timestamp": msg["timestamp"]
                }
                dialogues.append(dialogue)
            except:
                continue
        
        return {
            "total": len(dialogues),
            "dialogues": dialogues
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取对话失败: {}".format(str(e)))

@app.get("/speaker/{speaker_name}")
async def get_dialogues_by_speaker(speaker_name: str):
    """
    获取指定角色的所有对话
    
    - **speaker_name**: 角色名称（如：汤尚、周二、绑架犯、妈妈、小白）
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT * FROM conversation_messages 
            WHERE role = 'dialogue' AND content LIKE ?
            ORDER BY timestamp
        """, ("[{}说]: %".format(speaker_name),))
        
        messages = cursor.fetchall()
        conn.close()
        
        dialogues = []
        for msg in messages:
            try:
                metadata = json.loads(msg["metadata"]) if msg["metadata"] else {}
                content = msg["content"]
                if "]: " in content:
                    content = content.split("]: ", 1)[1]
                
                dialogue = {
                    "id": msg["id"],
                    "content": content,
                    "scene": metadata.get("scene", ""),
                    "sequence": metadata.get("sequence", 0),
                    "timestamp": msg["timestamp"]
                }
                dialogues.append(dialogue)
            except:
                continue
        
        return {
            "speaker": speaker_name,
            "total": len(dialogues),
            "dialogues": dialogues
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取角色对话失败: {}".format(str(e)))

@app.get("/scene/{scene_name}")
async def get_dialogues_by_scene(scene_name: str):
    """
    获取指定场景的所有对话
    
    - **scene_name**: 场景名称（如：地下室初次相遇、医院醒来等）
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT * FROM conversation_messages 
            WHERE role = 'dialogue'
            ORDER BY timestamp
        """)
        
        messages = cursor.fetchall()
        conn.close()
        
        dialogues = []
        for msg in messages:
            try:
                metadata = json.loads(msg["metadata"]) if msg["metadata"] else {}
                if scene_name in metadata.get("scene", ""):
                    content = msg["content"]
                    if "]: " in content:
                        content = content.split("]: ", 1)[1]
                    
                    dialogue = {
                        "id": msg["id"],
                        "speaker": metadata.get("speaker", "未知"),
                        "content": content,
                        "sequence": metadata.get("sequence", 0),
                        "timestamp": msg["timestamp"]
                    }
                    dialogues.append(dialogue)
            except:
                continue
        
        return {
            "scene": scene_name,
            "total": len(dialogues),
            "dialogues": dialogues
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取场景对话失败: {}".format(str(e)))

@app.get("/search")
async def search_dialogues(
    q: str = Query(..., description="搜索关键词"),
    limit: Optional[int] = Query(50, description="限制返回数量")
):
    """
    在《迷失》剧本对话中搜索关键词
    
    - **q**: 搜索关键词或短语  
    - **limit**: 限制返回的结果数量
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT * FROM conversation_messages 
            WHERE role = 'dialogue' AND content LIKE ?
            ORDER BY timestamp
            LIMIT ?
        """, ('%' + q + '%', limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        dialogues = []
        for msg in messages:
            try:
                metadata = json.loads(msg["metadata"]) if msg["metadata"] else {}
                content = msg["content"]
                if "]: " in content:
                    content = content.split("]: ", 1)[1]
                
                dialogue = {
                    "id": msg["id"],
                    "speaker": metadata.get("speaker", "未知"),
                    "content": content,
                    "scene": metadata.get("scene", ""),
                    "sequence": metadata.get("sequence", 0),
                    "timestamp": msg["timestamp"],
                    "match_highlight": content.replace(q, "**{}**".format(q)) if q in content else content
                }
                dialogues.append(dialogue)
            except:
                continue
        
        return {
            "query": q,
            "total": len(dialogues),
            "dialogues": dialogues
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="搜索失败: {}".format(str(e)))

@app.get("/speakers")
async def get_speakers():
    """获取《迷失》剧本中的所有角色列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT DISTINCT metadata FROM conversation_messages 
            WHERE role = 'dialogue' AND metadata IS NOT NULL
        """)
        
        messages = cursor.fetchall()
        conn.close()
        
        speakers = set()
        for msg in messages:
            try:
                metadata = json.loads(msg["metadata"])
                speaker = metadata.get("speaker")
                if speaker:
                    speakers.add(speaker)
            except:
                continue
        
        return {
            "total": len(speakers),
            "speakers": sorted(list(speakers))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取角色列表失败: {}".format(str(e)))

@app.get("/scenes")
async def get_scenes():
    """获取《迷失》剧本中的所有场景列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT DISTINCT metadata FROM conversation_messages 
            WHERE role = 'dialogue' AND metadata IS NOT NULL
        """)
        
        messages = cursor.fetchall()
        conn.close()
        
        scenes = set()
        for msg in messages:
            try:
                metadata = json.loads(msg["metadata"])
                scene = metadata.get("scene")
                if scene:
                    scenes.add(scene)
            except:
                continue
        
        return {
            "total": len(scenes),
            "scenes": sorted(list(scenes))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取场景列表失败: {}".format(str(e)))

@app.get("/stats")
async def get_stats():
    """获取《迷失》剧本的统计信息"""
    try:
        conn = get_db_connection()
        
        # 获取对话总数
        cursor = conn.execute("SELECT COUNT(*) as count FROM conversation_messages WHERE role = 'dialogue'")
        total_dialogues = cursor.fetchone()["count"]
        
        # 获取所有元数据
        cursor = conn.execute("""
            SELECT metadata FROM conversation_messages 
            WHERE role = 'dialogue' AND metadata IS NOT NULL
        """)
        messages = cursor.fetchall()
        conn.close()
        
        speakers = set()
        scenes = set()
        total_words = 0
        
        for msg in messages:
            try:
                metadata = json.loads(msg["metadata"])
                speaker = metadata.get("speaker")
                scene = metadata.get("scene")
                
                if speaker:
                    speakers.add(speaker)
                if scene:
                    scenes.add(scene)
                    
            except:
                continue
        
        return {
            "script_title": "《迷失》",
            "description": "多重人格少年被绑架的心理悬疑剧本",
            "total_dialogues": total_dialogues,
            "total_speakers": len(speakers),
            "total_scenes": len(scenes),
            "speakers": sorted(list(speakers)),
            "scenes": sorted(list(scenes)),
            "api_usage": {
                "get_all": "/dialogues",
                "by_speaker": "/speaker/汤尚",
                "by_scene": "/scene/地下室初次相遇", 
                "search": "/search?q=绑架",
                "speakers": "/speakers",
                "scenes": "/scenes"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取统计信息失败: {}".format(str(e)))

if __name__ == "__main__":
    import uvicorn
    
    print("🎭 启动《迷失》剧本对话API服务...")
    print("📡 API地址: http://localhost:8003")
    print("📚 API文档: http://localhost:8003/docs") 
    print("🔍 搜索示例: http://localhost:8003/search?q=汤尚")
    print("👥 角色列表: http://localhost:8003/speakers")
    print("🎬 场景列表: http://localhost:8003/scenes")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)
