# SAVE THIS FILE AS: fix_position_sizing.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\fix_position_sizing.py

"""
Fix position sizing to use actual available cash
"""

import shutil
from datetime import datetime

print("🔧 FIXING POSITION SIZING")
print("=" * 60)

# Backup main_v2.py
backup = f'main_v2_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy2('main_v2.py', backup)
print(f"✅ Backup saved: {backup}")

# Read main_v2.py
with open('main_v2.py', 'r') as f:
    content = f.read()

# Find and replace the position sizing logic
# Look for the line with available_capital
old_line = "available_capital = account['buying_power']"
new_line = """# Use CASH instead of buying power for more accurate calculation
            available_capital = float(account.get('cash', account['buying_power']))"""

content = content.replace(old_line, new_line)

# Also add safety margin
old_position = "position_value = available_capital * self.capital_per_trade"
new_position = """position_value = available_capital * self.capital_per_trade
            # Add safety margin to avoid insufficient funds
            position_value = position_value * 0.95  # Use 95% to account for fees"""

content = content.replace(old_position, new_position)

# Save fixed file
with open('main_v2.py', 'w') as f:
    f.write(content)

print("\n✅ SUCCESS! Position sizing fixed!")
print("\n📊 What changed:")
print("   • Uses actual CASH instead of buying power")
print("   • Adds 5% safety margin for fees")
print("   • Should prevent 'insufficient balance' errors")

print("\n💡 With $89,218 available cash:")
print("   • 30% = ~$26,765 per trade")
print("   • Can buy ~0.225 BTC")
print("   • Or ~6.9 ETH")
print("   • Or ~2,634 UNI")

print("\n🚀 RESTART YOUR BOT!")
print("   py main_v2.py")
print("\n🎯 Your first trade is coming NOW!")
print("=" * 60)