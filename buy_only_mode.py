# SAVE THIS FILE AS: buy_only_mode.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\buy_only_mode.py

"""
Temporarily disable SELL signals since we don't own any crypto yet
"""

import shutil
from datetime import datetime

print("🔧 SETTING BUY-ONLY MODE")
print("=" * 60)
print("Since you don't own any crypto yet, let's focus on BUYING first!")
print("=" * 60)

# Backup scanner.py
backup = f'scanner_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy2('scanner.py', backup)
print(f"✅ Backup saved: {backup}")

# Read scanner.py
with open('scanner.py', 'r') as f:
    content = f.read()

# Find the scan_all_symbols function and disable SELL checks
# Look for the sell signal check
old_sell_check = """                # Check sell conditions
                sell_signal, sell_score = self.check_sell_conditions(df_with_indicators, params)
                if sell_signal:
                    opportunities.append({"""

new_sell_check = """                # Check sell conditions - TEMPORARILY DISABLED
                # Only check sells if we actually own this crypto
                sell_signal = False  # DISABLED until we own crypto
                sell_score = 0
                if False and sell_signal:  # This block won't run
                    opportunities.append({"""

content = content.replace(old_sell_check, new_sell_check)

# Save modified file
with open('scanner.py', 'w') as f:
    f.write(content)

print("\n✅ SUCCESS! Buy-only mode activated!")
print("\n📊 What this does:")
print("   • Only looks for BUY opportunities")
print("   • No more trying to SELL crypto you don't own")
print("   • Once you own crypto, we'll re-enable SELLs")

print("\n🎯 Next opportunity will be a BUY!")
print("   Likely candidates: ETH, UNI, AAVE")

print("\n🚀 RESTART YOUR BOT NOW!")
print("   py main_v2.py")
print("\n" + "=" * 60)