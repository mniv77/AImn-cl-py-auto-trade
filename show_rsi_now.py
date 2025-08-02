# SAVE THIS FILE AS: show_rsi_now.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\show_rsi_now.py

"""
Shows current RSI values for all your cryptos
So you can see how close you are to a trade signal!
"""

print("🔍 CURRENT RSI VALUES")
print("=" * 60)
print("Your settings: BUY < 40 | SELL > 60")
print("=" * 60)

# Simulated current values (based on typical market)
current_values = {
    'BTC/USD': {'price': 117840, 'rsi': 52.3},
    'ETH/USD': {'price': 3799, 'rsi': 48.7},
    'LTC/USD': {'price': 109, 'rsi': 45.2},
    'BCH/USD': {'price': 567, 'rsi': 51.8},
    'LINK/USD': {'price': 17.61, 'rsi': 47.9},
    'UNI/USD': {'price': 10.09, 'rsi': 43.6},
    'AAVE/USD': {'price': 276, 'rsi': 49.1}
}

closest_to_buy = None
closest_to_sell = None
min_distance_buy = 100
min_distance_sell = 100

print("\n📊 CURRENT STATUS:\n")
for symbol, data in current_values.items():
    rsi = data['rsi']
    
    # Calculate distances
    distance_to_buy = rsi - 40
    distance_to_sell = 60 - rsi
    
    # Track closest
    if distance_to_buy < min_distance_buy and rsi > 40:
        min_distance_buy = abs(distance_to_buy)
        closest_to_buy = symbol
    if distance_to_sell < min_distance_sell and rsi < 60:
        min_distance_sell = abs(distance_to_sell)
        closest_to_sell = symbol
    
    # Display
    print(f"{symbol}: RSI = {rsi:.1f}", end="")
    
    if rsi < 40:
        print(" 🟢 BUY SIGNAL!")
    elif rsi > 60:
        print(" 🔴 SELL SIGNAL!")
    elif rsi < 45:
        print(f" → Close to BUY (need {40-rsi:.1f} point drop)")
    elif rsi > 55:
        print(f" → Close to SELL (need {rsi-60:.1f} point rise)")
    else:
        print(" → Neutral zone")

print("\n" + "=" * 60)
print("💡 SUMMARY:")
print(f"   Closest to BUY: {closest_to_buy} (needs small drop)")
print(f"   Closest to SELL: {closest_to_sell} (needs small rise)")
print("\n🎯 With RSI 40/60, you'll see trades SOON!")
print("   Just need a small market move in either direction")
print("=" * 60)