# patch_alpaca_connector.py
"""
Patches the get_bars method in alpaca_connector.py
"""

# Read the file
with open('alpaca_connector.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the get_bars method
in_get_bars = False
start_line = -1
indent = ""

for i, line in enumerate(lines):
    if 'def get_bars(self' in line:
        in_get_bars = True
        start_line = i
        # Get the indentation
        indent = line[:line.index('def')]
        break

if start_line == -1:
    print("❌ Could not find get_bars method")
else:
    # Insert the date import at the top if not already there
    has_datetime = False
    has_timedelta = False
    
    for line in lines[:20]:  # Check first 20 lines
        if 'from datetime import' in line:
            if 'datetime' in line:
                has_datetime = True
            if 'timedelta' in line:
                has_timedelta = True
    
    # Add imports if needed
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith('import') or line.startswith('from'):
            insert_pos = i + 1
    
    if not has_datetime or not has_timedelta:
        lines.insert(insert_pos, 'from datetime import datetime, timedelta\n')
    
    # Replace the problematic section in get_bars
    new_section = f'''
            # Get bars based on timeframe
            if timeframe == '1Day':
                # For daily bars, specify date range
                end = datetime.now()
                start = end - timedelta(days=limit * 2)  # Extra days for weekends
                bars = self.api.get_bars(
                    symbol,
                    alpaca_timeframe,
                    start=start.strftime('%Y-%m-%d'),
                    end=end.strftime('%Y-%m-%d'),
                    limit=limit,
                    adjustment='raw'
                ).df
            else:
                # For intraday bars, just use limit
                bars = self.api.get_bars(
                    symbol,
                    alpaca_timeframe,
                    limit=limit,
                    adjustment='raw'
                ).df
'''
    
    # Find where to insert this
    for i in range(start_line, len(lines)):
        if '# Get bars' in lines[i] or 'bars = self.api.get_bars' in lines[i]:
            # Find the end of this section
            j = i
            while j < len(lines) and not lines[j].strip().startswith('# Check if'):
                j += 1
            
            # Replace this section
            lines[i:j] = [new_section]
            break
    
    # Write back
    with open('alpaca_connector.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Patched alpaca_connector.py!")
    print("\nNow run: py test_aimn_system.py")