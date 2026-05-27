### Prerequisites
- Android device with Termux
- Telegram Bot Token (from @BotFather)
- Telegram Chat ID

### Installation

1. **Install Termux** from F-Droid (not Play Store)

2. **Open Termux and run:**
```bash
pkg update && pkg upgrade -y
pkg install python termux-api -y
pip install telebot requests pillow
termux-setup-storage

### Stop
ctrl+c
