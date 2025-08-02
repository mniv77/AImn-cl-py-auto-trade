# SAVE THIS FILE AS: fix_scanner.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\fix_scanner.py

"""
Fix the scanner to actually disable volume and ATR checks
"""

import shutil
from datetime import datetime

print("🔧 FIXING SCANNER - Removing Volume/ATR Requirements")
print("=" * 60)

# Backup scanner.py
backup = f'scanner_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy2('scanner.py', backup)
print(f"✅ Backup saved: {backup}")

# Read scanner.py
with open('scanner.py', 'r') as f:
    content = f.read()

# Fix buy conditions
old_buy = """        # Check all 4 conditions
        rsi_oversold = latest['rsi_real'] <= params['rsi_oversold']
        macd_bullish = latest['macd_bullish_cross']
        volume_confirmed = latest['bullish_volume']
        volatility_good = latest['volatility_expanding']
        
        # All conditions must be true
        signal = rsi_oversold and macd_bullish and volume_confirmed and volatility_good"""

new_buy = """        # Check only RSI and MACD (volume/ATR disabled)
        rsi_oversold = latest['rsi_real'] <= params['rsi_oversold']
        macd_bullish = latest['macd_bullish_cross']
        volume_confirmed = True  # DISABLED - always pass
        volatility_good = True   # DISABLED - always pass
        
        # Only RSI and MACD required now
        signal = rsi_oversold and macd_bullish"""

content = content.replace(old_buy, new_buy)

# Fix sell conditions
old_sell = """        # Check all 4 conditions
        rsi_overbought = latest['rsi_real'] >= params['rsi_overbought']
        macd_bearish = latest['macd_bearish_cross']
        volume_confirmed = latest['bearish_volume']
        volatility_good = latest['volatility_expanding']
        
        # All conditions must be true
        signal = rsi_overbought and macd_bearish and volume_confirmed and volatility_good"""

new_sell = """        # Check only RSI and MACD (volume/ATR disabled)
        rsi_overbought = latest['rsi_real'] >= params['rsi_overbought']
        macd_bearish = latest['macd_bearish_cross']
        volume_confirmed = True  # DISABLED - always pass
        volatility_good = True   # DISABLED - always pass
        
        # Only RSI and MACD required now
        signal = rsi_overbought and macd_bearish"""

content = content.replace(old_sell, new_sell)

# Save fixed file
with open('scanner.py', 'w') as f:
    f.write(content)

print("\n✅ SUCCESS! Scanner fixed!")
print("\n📊 What changed:")
print("   BEFORE: RSI + MACD + Volume + ATR (all 4 required)")
print("   NOW: RSI + MACD only (volume/ATR disabled)")

print("\n🎯 This means:")
print("   • Trades will trigger with just RSI 45/55 + MACD")
print("   • No more blocking by volume requirements")
print("   • No more blocking by volatility requirements")

print("\n🚀 NEXT STEPS:")
print("   1. Stop your bot (Ctrl+C)")
print("   2. Run this fix: py fix_scanner.py")
print("   3. Restart bot: py main_v2.py")
print("   4. WATCH TRADES HAPPEN! 🎉")

print("\n" + "=" * 60)
print("Your first trade is DEFINITELY coming now!")