# Albatros
Arbitrage bot for crypto exchanges 

This is an arbitrage trap to be used between two cryto currencies along two crypto exchanges.
It tries to take advantage of misplaced orders in narrow markets. You can set a margin between the current price in a narrow market, that can eventually be reached by a big order.
When that happen the bot executes an inverse market order at a market with a large liquidity.
My bot is setted to work between BitStamp (large liquidity) and Buda (low liquidity), with the BCH/BTC pair.
You could use it at any exchange and pair, but you would have to set all parameters manually.

This bot has gave me some satoshis in the past when used between Buda and QuadrigaCX, specially during high volatility periods.

This software is intented for fun, it's not well tested and should not be used for serious trading strategy.
