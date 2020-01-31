# Albatros
Arbitrage bot for crypto exchanges in Phyton 3

This is an arbitrage trap to be used between two cryto currencies along two crypto exchanges.
It tries to take advantage of misplaced orders in narrow markets. You can set a margin between the current trading price in the market and place limit orders that can eventually be reached by a big enoght market order. The bot will post limit orders on the narrow exchange, up and down the current trading price of the large echange, and wait for someone to take them. Price movements are constantly monitored and orders adjusted automatically.
When one of the orders is taken, the bot executes the inverse market order at the exchange with larger liquidity.
My bot is setted to work between BitStamp (large liquidity) and Buda (low liquidity), with the BCH/BTC pair.
You could use it at any exchange and pair, but you would have to set all parameters manually.

This bot has gave me some satoshis in the past when used between Buda and QuadrigaCX, specially during high volatility periods.

This software is intented for fun, it's not well tested and should not be taken for serious trading strategy.
