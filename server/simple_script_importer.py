#!/usr/bin/env python3
"""
简化版剧本对话导入工具 - 直接操作SQLite数据库
无需AI模型，直接将《迷失》剧本对话存储到数据库
"""
import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path

class SimpleScriptImporter:
    def __init__(self, db_path="data/conversations.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                script_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        """)
        
        # 创建消息表  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                content TEXT NOT NULL,
                role TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_id ON conversation_messages(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON conversation_messages(timestamp)")
        
        conn.commit()
        conn.close()
        print("✅ 数据库初始化完成")
    
    def create_session(self, session_id, user_id, script_content):
        """创建会话记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversation_sessions (id, user_id, script_content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, user_id, script_content, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
        return session_id
    
    def add_message(self, message_id, session_id, content, role, metadata):
        """添加消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversation_messages (id, session_id, content, role, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (message_id, session_id, content, role, datetime.now(), metadata))
        
        # 更新会话消息计数
        cursor.execute("""
            UPDATE conversation_sessions 
            SET message_count = (
                SELECT COUNT(*) FROM conversation_messages WHERE session_id = ?
            ),
            updated_at = ?
            WHERE id = ?
        """, (session_id, datetime.now(), session_id))
        
        conn.commit()
        conn.close()
    
    def get_session_messages(self, session_id):
        """获取会话消息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversation_messages 
            WHERE session_id = ? 
            ORDER BY timestamp
        """, (session_id,))
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages
    
    def search_messages(self, query=""):
        """搜索消息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if query:
            cursor.execute("""
                SELECT * FROM conversation_messages 
                WHERE content LIKE ? 
                ORDER BY timestamp
            """, ('%' + query + '%',))
        else:
            cursor.execute("""
                SELECT * FROM conversation_messages 
                ORDER BY timestamp
            """)
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages

def extract_dialogues():
    """提取《迷失》剧本中的对话内容"""
    dialogues = [
        {"speaker": "小白", "content": "旺旺旺旺。", "scene": "主人公醒来时"},
        {"speaker": "汤尚", "content": "你醒了？", "scene": "地下室初次相遇"},
        {"speaker": "汤尚", "content": "我叫汤尚，我从周三那里听说了你们七个人格的事情，你是周二？", "scene": "自我介绍"},
        {"speaker": "周二", "content": "嗯，我是周二，这是哪里？我就只记得我被人迷晕然后其他的事情我记不清了，这几天发生了什么？", "scene": "询问情况"},
        {"speaker": "汤尚", "content": "我在公园里面玩的时候走到了一个小山丘的后面，然后就感觉被人捂住了口鼻，随后意识模糊，就被绑架到这里了，在我来到这里的第二天你就被绑架过来了，我也不知道这是哪里，每天都有一个带着猪八戒的面具的人来给我们送饭，好像就是他把我们绑架到这里来的，他好像已经完全掌握了我们家里的联系方式，并且索要了一大笔钱财，但是不知道为什么还没有把我们放走，但是还好这个带着猪八戒面具的男人好像没有想伤害我们。", "scene": "解释绑架情况"},
        {"speaker": "周二", "content": "你这是什么意思？不来帮忙还嘲笑我？你难道不想出去吗？", "scene": "尝试撞门失败后的愤怒"},
        {"speaker": "汤尚", "content": "你们七个虽然是不同的七种人格，但是基本上醒来之后的都差不多，我的这些话在这几天里也已经重复说过好多遍了。我是想劝你别费力气了，那扇门是撞不开了，我们想要逃走也要像别的办法。", "scene": "劝阻撞门"},
        {"speaker": "绑架犯", "content": "吃吧。", "scene": "送饭时刻"},
        {"speaker": "汤尚", "content": "没事儿，他不会伤害我们的，自从来到这里已经差不多一个多星期了，他一直都是这样的，话不多说，每次都是过来送一个塑料袋的吃的然后就走了，基本上不会向我们透露一点点的信息，一开始还会向他问一些什么，但是他根本就不会理会我们说的话的。", "scene": "安慰周二"},
        {"speaker": "汤尚", "content": "吃吧。", "scene": "分享食物"},
        {"speaker": "汤尚", "content": "周五出去过的，那天那个绑架我们的人把周五绑出去了，周五回来的时候和我讲，那个绑架的人让他看了你们父母的在医院的一段视频，你们的母亲有了新的孩子，猪头脸还在一旁恐吓他，说如果你们的父母不愿意拿出赎金的话来救人的话，就会撕票。", "scene": "透露重要信息"},
        {"speaker": "汤尚", "content": "对不起，我知道这个消息对你来说很不可思议，但是周五要我一定要和你们都说，他说毕竟这是你们一起要面对的事情。", "scene": "道歉安慰"},
        {"speaker": "周二", "content": "我知道，还是谢谢你，如果没有你，我们肯定在这里过的更艰难，着空荡荡的昏暗的房间里面，起码还有一个人和我们一起，真的谢谢你。", "scene": "表达感谢"},
        {"speaker": "汤尚", "content": "周二，快点儿起来，我们已经找到了逃出去的办法。", "scene": "叫醒周二准备逃跑"},
        {"speaker": "周二", "content": "到底发生了什么？现在是晚上了吗？", "scene": "疑惑询问"},
        {"speaker": "汤尚", "content": "已经又过的一个星期了，在这一个星期里面发生了很多的事情，猪头脸会不定时的把我们拽到楼上去，周一偷到了备用钥匙，我们要趁着猪头脸还没察觉出来赶紧逃走。", "scene": "解释逃跑计划"},
        {"speaker": "绑架犯", "content": "你们两个站住，你们跑不掉的。", "scene": "追赶逃跑者"},
        {"speaker": "妈妈", "content": "宝贝，你醒了，你终于醒来了，医生说只要醒过来了就是没事儿了。", "scene": "医院醒来"}
    ]
    return dialogues

def main():
    print("🎭 《迷失》剧本对话数据库导入工具")
    print("=" * 50)
    
    # 初始化导入器
    importer = SimpleScriptImporter()
    
    # 创建会话
    session_id = str(uuid.uuid4())
    user_id = "script_user_001"
    script_content = "《迷失》- 一个关于多重人格少年被绑架后的心理悬疑剧本"
    
    print("🎭 开始导入《迷失》剧本对话内容...")
    
    # 创建会话记录
    importer.create_session(session_id, user_id, script_content)
    print("✅ 会话创建成功: {}".format(session_id))
    
    # 导入对话
    dialogues = extract_dialogues()
    imported_count = 0
    
    for i, dialogue in enumerate(dialogues):
        message_id = str(uuid.uuid4())
        content = "[{}说]: {}".format(dialogue["speaker"], dialogue["content"])
        
        metadata = {
            "speaker": dialogue["speaker"],
            "scene": dialogue["scene"],
            "sequence": i + 1,
            "script_title": "《迷失》"
        }
        
        importer.add_message(
            message_id=message_id,
            session_id=session_id,
            content=content,
            role="dialogue",
            metadata=json.dumps(metadata, ensure_ascii=False)
        )
        
        imported_count += 1
        print("  📝 导入对话 {}: {} - {}".format(i+1, dialogue["speaker"], dialogue["content"][:30] + "..."))
    
    print()
    print("🎉 《迷失》剧本导入完成!")
    print("📊 导入统计:")
    print("  - 会话ID: {}".format(session_id))
    print("  - 对话数量: {} 条".format(imported_count))
    print("  - 角色数量: {} 个".format(len(set(d["speaker"] for d in dialogues))))
    
    # 导出数据供协作者使用
    print()
    print("📤 导出数据供协作者使用...")
    messages = importer.get_session_messages(session_id)
    
    export_data = {
        "script_info": {
            "title": "《迷失》",
            "session_id": session_id,
            "total_dialogues": len(messages),
            "export_time": datetime.now().isoformat()
        },
        "dialogues": messages
    }
    
    export_file = Path("database_exports") / "script_lost_dialogues_{}.json".format(
        datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    export_file.parent.mkdir(exist_ok=True)
    
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 数据已导出: {}".format(export_file))
    
    print()
    print("🎯 接下来可以做的:")
    print("1. 启动数据库API: python database_only_main.py")
    print("2. 查看API文档: http://localhost:8001/docs")
    print("3. 测试搜索: http://localhost:8001/api/v1/conversation/search?query=汤尚")
    print("4. 创建协作者包: python share_database.py --yes")
    
    return session_id

if __name__ == "__main__":
    main()
