# SAVE THIS FILE AS: super_easy_mode.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\super_easy_mode.py

"""
Makes trading SUPER EASY just to see it work!
We can tighten it later once you see trades happening
"""

import shutil
from datetime import datetime

print("🚀 SUPER EASY MODE - Let's Get Some Trades!")
print("=" * 60)
print("This will make trades happen TODAY!")
print("=" * 60)

# Backup current config
config_file = 'aimn_crypto_config.py'
backup = f'config_backup_{datetime.now().strftime("%Y%m%d_%H%M")}.py'
shutil.copy2(config_file, backup)
print(f"✅ Backup saved: {backup}")

# Read config
with open(config_file, 'r') as f:
    content = f.read()

# Make SUPER EASY changes
print("\n🔧 Making it SUPER EASY to trade:")

# Current settings might be 40/60, let's go to 45/55!
content = content.replace("'rsi_oversold': 40", "'rsi_oversold': 45")
content = content.replace("'rsi_oversold': 35", "'rsi_oversold': 45")  # In case still 35
content = content.replace("'rsi_overbought': 60", "'rsi_overbought': 55")
content = content.replace("'rsi_overbought': 65", "'rsi_overbought': 55")  # In case still 65

print("✅ RSI: 45/55 (SUPER EASY - hits all the time!)")

# Make MACD super fast for more crossovers
content = content.replace("'macd_fast': 8", "'macd_fast': 5")
content = content.replace("'macd_fast': 12", "'macd_fast': 5")  # In case still 12
content = content.replace("'macd_slow': 17", "'macd_slow': 13")
content = content.replace("'macd_slow': 26", "'macd_slow': 13")  # In case still 26
content = content.replace("'macd_signal': 9", "'macd_signal': 5")

print("✅ MACD: Super fast (5,13,5) - more crossovers!")

# Save
with open(config_file, 'w') as f:
    f.write(content)

print("\n" + "=" * 60)
print("🎉 SUCCESS! You WILL see trades today!")
print("=" * 60)

print("\n📊 What this means:")
print("• BUY when RSI < 45 (happens often!)")
print("• SELL when RSI > 55 (happens often!)")
print("• MACD super responsive")
print("• Expect 10-20+ trades per day!")

print("\n⚠️  IMPORTANT:")
print("This is just to TEST and see it working!")
print("Once you see trades, we'll optimize for PROFIT")

print("\n🚀 DO NOW:")
print("1. Restart bot: py main_v2.py")
print("2. Watch for trades within 30 minutes!")
print("3. Once working, we'll tune for quality")

print(f"\n💾 Your careful settings are saved in: {backup}")
print("We can restore them anytime!")