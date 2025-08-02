"""
Script to automatically update RSI settings in your config
This will change RSI from 30/70 to 35/65 for more trading opportunities
"""

import os
import shutil
from datetime import datetime

print("🔧 RSI Settings Updater")
print("=" * 60)
print("This will update your RSI settings from 30/70 to 35/65")
print("This should give you more trading opportunities!")
print("=" * 60)

# File paths
config_file = 'aimn_crypto_config.py'
backup_file = f'aimn_crypto_config_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'

# Check if config exists
if not os.path.exists(config_file):
    print(f"❌ Error: {config_file} not found!")
    print("Make sure you're in the correct directory: C:\\Users\\mniv7\\Documents\\meir\\cl-py")
    exit(1)

# Create backup
print(f"\n📁 Creating backup: {backup_file}")
shutil.copy2(config_file, backup_file)
print("✅ Backup created successfully!")

# Read the config file
print(f"\n📖 Reading {config_file}...")
with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Count how many changes we'll make
original_oversold_count = content.count("'rsi_oversold': 30")
original_overbought_count = content.count("'rsi_overbought': 70")

print(f"\n🔍 Found:")
print(f"   - {original_oversold_count} instances of 'rsi_oversold': 30")
print(f"   - {original_overbought_count} instances of 'rsi_overbought': 70")

# Make the changes
print("\n✏️ Updating RSI values...")
new_content = content.replace("'rsi_oversold': 30", "'rsi_oversold': 35")
new_content = new_content.replace("'rsi_overbought': 70", "'rsi_overbought': 65")

# Verify changes
new_oversold_count = new_content.count("'rsi_oversold': 35")
new_overbought_count = new_content.count("'rsi_overbought': 65")

# Write the updated content
print("\n💾 Saving changes...")
with open(config_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\n✅ Success! Configuration updated:")
print(f"   - Changed {new_oversold_count} oversold values: 30 → 35")
print(f"   - Changed {new_overbought_count} overbought values: 70 → 65")

print("\n📊 What this means:")
print("   - BUY signals: Now triggers at RSI < 35 (was < 30)")
print("   - SELL signals: Now triggers at RSI > 65 (was > 70)")
print("   - Result: About 3-5x more trading opportunities!")

print("\n🚀 Next steps:")
print("   1. Stop your bot (Ctrl+C)")
print("   2. Restart it: py main_v2.py")
print("   3. Watch for more trading signals!")

print("\n💡 Tips:")
print("   - If still too few trades, try 40/60")
print("   - If too many trades, go back to 33/67")
print(f"   - Your backup is saved as: {backup_file}")

print("\n" + "=" * 60)
print("🎯 Configuration update complete!")
print("=" * 60)

# Show a preview of what changed
print("\n📋 Preview of changes:")
print("Old: 'rsi_oversold': 30  →  New: 'rsi_oversold': 35")
print("Old: 'rsi_overbought': 70  →  New: 'rsi_overbought': 65")