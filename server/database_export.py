#!/usr/bin/env python3
"""
数据库导出工具 - 为协作者提供数据库备份和同步功能
"""
import sqlite3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse

class DatabaseExporter:
    def __init__(self, db_path: str = "data/conversations.db"):
        self.db_path = Path(db_path)
        self.backup_dir = Path("database_exports")
        self.backup_dir.mkdir(exist_ok=True)
        
    def export_database(self, output_path: Optional[str] = None) -> str:
        """导出完整数据库文件"""
        if not self.db_path.exists():
            print("❌ 数据库文件不存在，创建空数据库...")
            self._create_empty_database()
            
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.backup_dir / f"conversations_backup_{timestamp}.db"
        else:
            output_path = Path(output_path)
            
        # 复制数据库文件
        shutil.copy2(self.db_path, output_path)
        print(f"✅ 数据库已导出到: {output_path}")
        return str(output_path)
        
    def export_to_json(self, output_path: Optional[str] = None) -> str:
        """导出数据库内容为JSON格式"""
        if not self.db_path.exists():
            print("❌ 数据库文件不存在")
            return ""
            
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.backup_dir / f"conversations_data_{timestamp}.json"
        else:
            output_path = Path(output_path)
            
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式的行
        
        data = {
            "export_time": datetime.now().isoformat(),
            "sessions": [],
            "messages": []
        }
        
        try:
            # 导出会话数据
            cursor = conn.execute("SELECT * FROM conversation_sessions")
            sessions = cursor.fetchall()
            data["sessions"] = [dict(row) for row in sessions]
            
            # 导出消息数据
            cursor = conn.execute("SELECT * FROM conversation_messages ORDER BY timestamp")
            messages = cursor.fetchall()
            data["messages"] = [dict(row) for row in messages]
            
            # 写入JSON文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                
            print(f"✅ 数据已导出为JSON: {output_path}")
            print(f"📊 导出统计: {len(data['sessions'])} 个会话, {len(data['messages'])} 条消息")
            
        except sqlite3.Error as e:
            print(f"❌ 导出失败: {e}")
            return ""
        finally:
            conn.close()
            
        return str(output_path)
        
    def import_from_json(self, json_path: str) -> bool:
        """从JSON文件导入数据"""
        json_path = Path(json_path)
        if not json_path.exists():
            print(f"❌ JSON文件不存在: {json_path}")
            return False
            
        # 确保数据库存在
        if not self.db_path.exists():
            self._create_empty_database()
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            conn = sqlite3.connect(self.db_path)
            
            # 导入会话数据
            sessions = data.get("sessions", [])
            for session in sessions:
                conn.execute("""
                    INSERT OR REPLACE INTO conversation_sessions 
                    (id, user_id, script_content, created_at, updated_at, message_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session["id"], session["user_id"], session["script_content"],
                    session["created_at"], session["updated_at"], session["message_count"]
                ))
                
            # 导入消息数据
            messages = data.get("messages", [])
            for message in messages:
                conn.execute("""
                    INSERT OR REPLACE INTO conversation_messages
                    (id, session_id, content, role, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    message["id"], message["session_id"], message["content"],
                    message["role"], message["timestamp"], message["metadata"]
                ))
                
            conn.commit()
            conn.close()
            
            print(f"✅ 数据导入成功!")
            print(f"📊 导入统计: {len(sessions)} 个会话, {len(messages)} 条消息")
            return True
            
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return False
            
    def import_database(self, db_path: str) -> bool:
        """导入数据库文件"""
        source_path = Path(db_path)
        if not source_path.exists():
            print(f"❌ 源数据库文件不存在: {source_path}")
            return False
            
        try:
            # 备份现有数据库
            if self.db_path.exists():
                backup_path = self.backup_dir / f"backup_before_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(self.db_path, backup_path)
                print(f"📦 已备份现有数据库到: {backup_path}")
                
            # 复制新数据库
            self.db_path.parent.mkdir(exist_ok=True)
            shutil.copy2(source_path, self.db_path)
            print(f"✅ 数据库导入成功: {self.db_path}")
            return True
            
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return False
            
    def _create_empty_database(self):
        """创建空的数据库结构"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        
        # 创建表结构
        conn.executescript("""
            -- 会话表
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                script_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0
            );
            
            -- 消息表
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                content TEXT NOT NULL,
                role TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
            );
            
            -- 创建索引
            CREATE INDEX IF NOT EXISTS idx_messages_session_id ON conversation_messages(session_id);
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON conversation_messages(timestamp);
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON conversation_sessions(user_id);
        """)
        
        conn.commit()
        conn.close()
        print(f"✅ 已创建空数据库: {self.db_path}")
        
    def list_exports(self):
        """列出所有导出文件"""
        if not self.backup_dir.exists():
            print("📁 暂无导出文件")
            return
            
        files = list(self.backup_dir.glob("*"))
        if not files:
            print("📁 暂无导出文件")
            return
            
        print(f"📁 导出文件列表 ({self.backup_dir}):")
        for file in sorted(files):
            size = file.stat().st_size
            modified = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"  📄 {file.name} ({size:,} bytes, {modified.strftime('%Y-%m-%d %H:%M:%S')})")

def main():
    parser = argparse.ArgumentParser(description="数据库导出导入工具")
    parser.add_argument("--action", choices=["export", "export-json", "import", "import-json", "list"], 
                       required=True, help="操作类型")
    parser.add_argument("--input", help="输入文件路径")
    parser.add_argument("--output", help="输出文件路径") 
    parser.add_argument("--db", default="data/conversations.db", help="数据库路径")
    
    args = parser.parse_args()
    
    exporter = DatabaseExporter(args.db)
    
    if args.action == "export":
        exporter.export_database(args.output)
    elif args.action == "export-json":
        exporter.export_to_json(args.output)
    elif args.action == "import":
        if not args.input:
            print("❌ 请指定输入文件 --input")
            return
        exporter.import_database(args.input)
    elif args.action == "import-json":
        if not args.input:
            print("❌ 请指定输入文件 --input")
            return
        exporter.import_from_json(args.input)
    elif args.action == "list":
        exporter.list_exports()

if __name__ == "__main__":
    main()
