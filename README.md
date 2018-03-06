# Bittrex-Auto-Blacklist
Profit Trailer tool designed to detect new coins and blacklist them.

Feel free to use this in your own projects! I just developed this as a little hobby project. May or may not be maintained.

If you find this tool to be useful, please consider buying me a beer (or help me not drown in my student loan payments) by donating here:

ZEN: znaHwdLYPVMcgoSwsP7jz6ryie9hgdDJebk

LTC: LQJcpD6ksr73JuPE5VQjBxLYdPse44yzkT

# Requirements
Developed using Python 3.6.2. Use pip to install missing modules.

1. Module: requests

# Usage
Install bittrex_auto_blacklist.py in the same folder as PAIRS.properties. <b>Make sure you make a backup of PAIRS.properties!</b>. It's good practice in general, but seriously don't skip out on this to be safe!

Example: python bittrex_auto_blacklist.py

1. Generates a market-specific coin log (BTC/ETH) csv.
2. Generates a blacklist using the specified age as an input (default: 30 days)
3. If changes are found, then creates/modifies the following section in PAIRS.properties (with sample items!):

\# [Start Bittrex Auto Blacklist]<br />
ETH_ZRX_trading_enabled=false<br />
ETH_VEE_trading_enabled=false<br />
ETH_TRX_trading_enabled=false<br />
ETH_BCPT_trading_enabled=false<br />
ETH_WAX_trading_enabled=false<br />
ETH_SRN_trading_enabled=false<br />
\# [End Bittrex Auto Blacklist]

4. Wait for the next heartbeat (default: 60 seconds)

This was tested with ETH markets, but it should work for BTC markets. Until I create a proper config file, just modify the settings section at the top of the script.
