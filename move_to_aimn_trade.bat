@echo off
echo Moving remaining AIMn files...

:: Move config (rename if needed)
if exist config.py (
    move config.py ..\AIMn-Trade\app\
    echo Moved: config.py
) else if exist aimn_crypto_config.py (
    move aimn_crypto_config.py ..\AIMn-Trade\app\config.py
    echo Renamed and moved: aimn_crypto_config.py -> config.py
) else (
    echo NOT FOUND: config.py or aimn_crypto_config.py
)

:: Move trade log files
if exist aimn_trades.json (
    move aimn_trades.json ..\AIMn-Trade\data\
    echo Moved: aimn_trades.json
) else (
    echo NOT FOUND: aimn_trades.json
)

if exist aimn_crypto_trading.log (
    move aimn_crypto_trading.log ..\AIMn-Trade\data\
    echo Moved: aimn_crypto_trading.log
) else (
    echo NOT FOUND: aimn_crypto_trading.log
)

:: Move dashboard
if exist aimn_working_dashboard.py (
    move aimn_working_dashboard.py ..\AIMn-Trade\dashboard\
    echo Moved: aimn_working_dashboard.py
) else if exist aimn_dashboard.py (
    move aimn_dashboard.py ..\AIMn-Trade\dashboard\
    echo Moved: aimn_dashboard.py
) else (
    echo NOT FOUND: aimn dashboard file
)