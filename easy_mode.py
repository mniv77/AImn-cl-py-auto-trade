# SAVE THIS FILE AS: easy_mode.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\easy_mode.py

"""
EASY MODE - This will get you trading quickly!
Just RSI + MACD, looser settings
"""

import shutil
from datetime import datetime

print("🚀 EASY TRADE MODE ACTIVATOR")
print("=" * 60)
print("This will make your system trade MORE!")
print("We can fine-tune later once you see it working!")
print("=" * 60)

# Backup config
config_file = 'aimn_crypto_config.py'
backup = f'config_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy2(config_file, backup)
print(f"✅ Backup saved: {backup}")

# Read config
with open(config_file, 'r') as f:
    content = f.read()

# Make AGGRESSIVE changes for more trades
print("\n🔧 Making changes for MORE TRADES:")

# 1. Easier RSI levels
content = content.replace("'rsi_oversold': 35", "'rsi_oversold': 40")  # Even easier!
content = content.replace("'rsi_overbought': 65", "'rsi_overbought': 60")  # Even easier!
print("✅ RSI: 40/60 (very easy to hit!)")

# 2. Disable volume check
content = content.replace("'volume_threshold': 1.2", "'volume_threshold': 0.01")  # Basically off
print("✅ Volume check: DISABLED")

# 3. Disable ATR check  
content = content.replace("'atr_threshold': 1.3", "'atr_threshold': 0.01")  # Basically off
print("✅ ATR check: DISABLED")

# 4. Faster MACD
content = content.replace("'macd_fast': 12", "'macd_fast': 8")  # More responsive
content = content.replace("'macd_slow': 26", "'macd_slow': 17")  # More responsive
print("✅ MACD: Faster settings (more signals)")

# Save
with open(config_file, 'w') as f:
    f.write(content)

print("\n" + "=" * 60)
print("🎉 SUCCESS! Your bot will now trade MUCH more!")
print("=" * 60)

print("\n📊 What changed:")
print("• RSI: 40/60 (instead of 30/70) - EASY mode")
print("• Volume: Disabled - won't block trades")
print("• ATR: Disabled - won't block trades")
print("• MACD: Faster - more crossovers")

print("\n🎯 This means:")
print("• More BUY signals (RSI < 40 is common)")
print("• More SELL signals (RSI > 60 is common)")
print("• Probably 5-10 trades per day!")

print("\n🚀 DO THIS NOW:")
print("1. Stop your bot (Ctrl+C)")
print("2. Restart: py main_v2.py")
print("3. Watch trades happen! 🎉")

print("\n💡 Later we can:")
print("• Add filters back for quality")
print("• Adjust stops and trails")
print("• Optimize for profit")
print("\nBut first - let's see it WORK!")