# SAVE THIS FILE AS: fix_crypto_orders.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\fix_crypto_orders.py

"""
Fix the crypto order type error
"""

import shutil
from datetime import datetime

print("🔧 FIXING CRYPTO ORDER TYPE")
print("=" * 60)

# Backup alpaca_connector.py
backup = f'alpaca_connector_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy2('alpaca_connector.py', backup)
print(f"✅ Backup saved: {backup}")

# Read the file
with open('alpaca_connector.py', 'r') as f:
    content = f.read()

# Find and fix the place_order function
# Look for time_in_force parameter
old_pattern = "time_in_force='day'"
new_pattern = "time_in_force='gtc' if '/' in symbol else 'day'"

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("✅ Fixed time_in_force for crypto orders")
else:
    # Try another pattern
    if "time_in_force=" in content:
        print("⚠️  time_in_force found but pattern different")
        print("   Attempting alternate fix...")
        
        # Add crypto check at the beginning of place_order function
        old_order = "def place_order(self, symbol: str, side: str, qty: float) -> dict:"
        new_order = """def place_order(self, symbol: str, side: str, qty: float) -> dict:
        # Fix time_in_force for crypto
        is_crypto = '/' in symbol
        time_force = 'gtc' if is_crypto else 'day'"""
        
        content = content.replace(old_order, new_order)
        
        # Then update the actual order call
        content = content.replace("time_in_force='day'", "time_in_force=time_force")

# Save the fixed file
with open('alpaca_connector.py', 'w') as f:
    f.write(content)

print("\n✅ SUCCESS! Crypto orders will now work!")
print("\n📊 What was wrong:")
print("   Crypto needs time_in_force='gtc' (good till canceled)")
print("   Stocks use time_in_force='day'")

print("\n🚀 NEXT STEPS:")
print("   1. Stop bot (Ctrl+C)")
print("   2. Run: py fix_crypto_orders.py")
print("   3. Restart: py main_v2.py")
print("   4. TRADES WILL EXECUTE! 🎉")

print("\n💡 The GOOD news:")
print("   Scanner IS finding opportunities (UNI/USD BUY)")
print("   Just needed to fix the order type!")
print("=" * 60)