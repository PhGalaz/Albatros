from configparser import ConfigParser
import ccxt
import time

parser = ConfigParser()
parser.read('keys.conf')

###BUDA
buda = ccxt.buda({
	'apiKey': parser.get('Buda', 'api_key'),
	'secret': parser.get('Buda', 'api_secret'),
})
BU_balance_btc = buda.fetch_balance()['BTC']['free']
BU_balance_bch = buda.fetch_balance()['BCH']['free']
print ('BALANCE BUDA BTC :', BU_balance_btc)
print ('BALANCE BUDA BCH :', BU_balance_bch)

###BITSTAMP
bitstamp = ccxt.bitstamp({
	'uid': parser.get('Bitstamp', 'user'),
	'apiKey': parser.get('Bitstamp', 'key'),
	'secret': parser.get('Bitstamp', 'secret'),
	'enableRateLimit': 'true', 
})
BI_balance_btc = bitstamp.fetch_balance()['BTC']['free']
BI_balance_bch = bitstamp.fetch_balance()['BCH']['free']
print ('BALANCE BITSTAMP BTC :', BI_balance_btc)
print ('BALANCE BITSTAMP BCH :', BI_balance_bch)

#Totals
BTC_T = round(BU_balance_btc + BI_balance_btc, 8)
BCH_T = BU_balance_bch + BI_balance_bch
print ("Total BTC : %f   /  Total BCH : %f" % (BTC_T, BCH_T))

#Variables
switchA = False
switchB = False
BIDid = None
ASKid = None
poolA = 0
poolB = 0
idx = 0

# Set spread to best order to 25%
params = 0.25

#Functions

def Pre_Bid():
	while True:
		try:
			bid_best_price = bitstamp.fetch_order_book(bitstamp.symbols[0])['bids'][0][0]
			amount = buda.fetch_balance()['BTC']['free']
			BI_balance_bch = bitstamp.fetch_balance()['BCH']['free']
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			continue
		break	
	price_to_offer = round(bid_best_price * (1 - params), 8)
	amount = round((amount / price_to_offer) - 0.00000001, 8)
	if amount > BI_balance_bch:
		amount = round(BI_balance_bch - 0.00000001, 8)
	Post_Bid(amount, price_to_offer)

def Pre_Ask():
	while True:
		try:
			ask_best_price = bitstamp.fetch_order_book(bitstamp.symbols[0])['bids'][0][0]
			amount = buda.fetch_balance()['BCH']['free']
			BI_balance_btc = bitstamp.fetch_balance()['BTC']['free']
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			continue
		break		
	price_to_offer = round(ask_best_price * (1 + params), 8)
	amount = round(amount * price_to_offer, 8)
	if amount > BI_balance_btc:
		amount = round(BI_balance_btc / price_to_offer, 8) - 0.00000001
	Post_Ask(amount, price_to_offer)

def Post_Bid(trade, offer):
	global switchA
	if switchA == True:
		global BIDid
		while True:
			try:
				buda.cancelOrder(BIDid)
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			except (ccxt.OrderNotFound) as error:
				break
			break				
		time.sleep(3)
	while True:
		try:
			BU_balance_btc = buda.fetch_balance()['BTC']['free']
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			continue
		break			
	if BU_balance_btc < 0.00000002:
		print ('Not enough BTC funds on BUDA')
		exit()
	while True:
		while True:
			try:
				a = buda.fetchBalance
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			break
		try:
			order = buda.createLimitBuyOrder ('BCH/BTC', trade, offer)
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			while True:
				try:
					b = buda.fetchBalance
				except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
					continue
				break
			if a == b:
				continue
			else:
				break
		break				
	Def_Id_A(order['id'])
	print (order)
	Def_SwitchA(True)

def Post_Ask(trade, offer):
	global switchB
	if switchB == True:
		global ASKid
		while True:
			try:
				buda.cancelOrder(ASKid)
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			except (ccxt.OrderNotFound) as error:
				break
			break				
		time.sleep(3)
	while True:
		try:
			BU_balance_bch = buda.fetch_balance()['BCH']['free']
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			continue
		break
	if BU_balance_bch < 0.00000002:
		print ('Not enough BCH funds on BUDA')
		exit()
	while True:
		while True:
			try:
				a = buda.fetchBalance
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			break
		try:
			order = buda.createLimitSellOrder ('BCH/BTC', trade, offer)
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			while True:
				try:
					b = buda.fetchBalance
				except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
					continue
				break
			if a == b:
				continue
			else:
				break
		break		
	Def_Id_B(order['id'])
	print (order)
	Def_SwitchB(True)

def Def_SwitchA(modo):
	global switchA
	switchA = modo

def Def_SwitchB(modo):
	global switchB
	switchB = modo

def Def_Id_A(id_):
	global BIDid
	BIDid = id_

def Def_Id_B(id_):
	global ASKid
	ASKid = id_

def Post_Market_Order_A(trade):
	global poolA
	while True:
		try:
			lst = bitstamp.fetchTicker('BCH/BTC')['last']
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			continue
		break
	if trade < 0.001 / lst:
		poolA = poolA + trade
		return
	elif poolA != 0 and poolA + trade > 0.001 / lst:
		while True:
			while True:
				try:
					a = buda.fetchBalance
				except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
					continue
				break
			try:
				order = bitstamp.createMarketSellOrder ('BCH/BTC', trade + poolA)
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				while True:
					try:
						b = buda.fetchBalance
					except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
						continue
					break
				if a == b:
					continue
				else:
					break
			break
		poolA = 0
	else:
		while True:
			while True:
				try:
					a = buda.fetchBalance
				except (ccxt.RequestTimeout, ccxt.NetworkError) as error:
					continue
				break
			try:
				bitstamp.createMarketSellOrder ('BCH/BTC', trade + poolA)
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				while True:
					try:
						b = buda.fetchBalance
					except (ccxt.RequestTimeout, ccxt.NetworkError) as error:
						continue
					break
				if a == b:
					continue
				else:
					break
			break
		poolA = 0
	while True:
		try:
			NewBalanceBTC = buda.fetch_balance()['BTC']['free'] + bitstamp.fetch_balance()['BTC']['free']
			NewBalanceBCH = buda.fetch_balance()['BCH']['free'] + bitstamp.fetch_balance()['BCH']['free']
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			continue
		break
	diffBTC = NewBalanceBTC - BTC_T
	diffBCH = NewBalanceBCH - BCH_T
	print ('Nuevo Balance BTC =', NewBalanceBTC, '. Margen : ', diffBTC)
	print ('Nuevo Balance BCH =', NewBalanceBCH, '. Margen : ', diffBCH)
	if diffBCH < 0 or diffBTC < 0:
		print ('FATAL ERROR')
		exit()
	BTC_T = NewBalanceBTC
	BCH_T = NewBalanceBCH

def Post_Market_Order_B(trade):
	global poolB
	while True:
		try:
			lst = bitstamp.fetchTicker('BCH/BTC')['last']
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			continue
		break
	if trade < 0.001 / lst:
		poolB = poolB + trade
		return
	elif poolB != 0 and poolB + trade > 0.001 / lst:
		while True:
			while True:
				try:
					a = buda.fetchBalance
				except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
					continue
				break
			try:
				order = bitstamp.createMarketBuyOrder ('BCH/BTC', trade + poolB)
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				while True:
					try:
						b = buda.fetchBalance
					except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
						continue
					break
				if a == b:
					continue
				else:
					break
			break
		poolB = 0
	else:
		while True:
			while True:
				try:
					a = buda.fetchBalance
				except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
					continue
				break
			try:
				bitstamp.createMarketBuyOrder ('BCH/BTC', trade + poolB)
			except (ccxt.RequestTimeout, ccxt.NetworkError) as error:
				while True:
					try:
						b = buda.fetchBalance
					except (ccxt.RequestTimeout, ccxt.NetworkError) as error:
						continue
					break
				if a == b:
					continue
				else:
					break
			break		
		poolB = 0
	while True:
		try:
			NewBalanceBTC = buda.fetch_balance()['BTC']['free'] + bitstamp.fetch_balance()['BTC']['free']
			NewBalanceBCH = buda.fetch_balance()['BCH']['free'] + bitstamp.fetch_balance()['BCH']['free']
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			continue
		break	
	diffBTC = NewBalanceBTC - BTC_T
	diffBCH = NewBalanceBCH - BCH_T
	print ('Nuevo Balance BTC =', NewBalanceBTC, '. Margen : ', diffBTC)
	print ('Nuevo Balance BCH =', NewBalanceBCH, '. Margen : ', diffBCH)
	if diffBCH < 0 or diffBTC < 0:
		print ('FATAL ERROR')
		exit()
	BTC_T = NewBalanceBTC
	BCH_T = NewBalanceBCH

#Main
while True:
	try:
		best_priceA = bitstamp.fetch_order_book(bitstamp.symbols[0])['bids'][0][0]
		best_priceB = bitstamp.fetch_order_book(bitstamp.symbols[0])['asks'][0][0]
	except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
		continue
	break
total_traded_ask = 0.0
total_traded_bid = 0.0
times = 0
reset = 0
Pre_Bid()
Pre_Ask()

while True:
	while True:
		try:
			detailsA = buda.fetch_order(BIDid)
			detailsB = buda.fetch_order(ASKid)
			statusA = detailsA['status']
			statusB = detailsB['status']
			tradedA = detailsA['info']['traded_amount'][0]
			tradedB = detailsB['info']['traded_amount'][0]
		except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
			continue
		break

	if tradedA != total_traded_ask and statusA == 'pending':
		tradeA = float(tradedA) - float(total_traded_ask)
		while True:	
			try:
				BI_balance_bch = bitstamp.fetch_balance()['BCH']['free']
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			break				
		if tradeA > BI_balance_bch:
			print ('No more BCH on Bitstamp')
			Post_Market_Order_A(BI_balance_bch)
			exit()
		tradeA = round(tradeA * 1.008, 8)
		Post_Market_Order_A(tradeA)
		total_traded_ask = tradedA

	if tradedB != total_traded_bid and statusB == 'pending':
		tradeB = float(tradedB) - float(total_traded_bid)
		while True:	
			try:
				BI_balance_btc = bitstamp.fetch_balance()['BTC']['free']
				to_spend = tradeB * bitstamp.fetch_order_book(bitstamp.symbols[0])['asks'][0][0] 
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			break			
		if to_spend > BI_balance_btc:
			print ('No more BTC on Bitstamp')
			while True:	
				try:
					avai = round(round(BI_balance_btc / (float(bitstamp.fetch_order_book(bitstamp.symbols[0])['asks'][0][0])), 8) * 0.998 - 0.00000001, 8)
				except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
					continue
				break		
			Post_Market_Order_B(avai)
			exit()
		tradeB = round(tradeB * 1.008, 8)
		Post_Market_Order_B(tradeB)
		total_traded_bid = tradedB

	if statusA == 'traded':
		tradeA = tradedA - tradedAac
		while True:	
			try:
				BI_balance_bch = bitstamp.fetch_balance()['BCH']['free']
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			break			
		if tradeA > BI_balance_bch:
			print ('No more BCH on Bitstamp')
			Post_Market_Order_A(BI_balance_bch)
			exit()
		tradeA = round(tradeA * 1.008, 8)
		Post_Market_Order_A(tradeA)
		total_traded_ask = 0
		switchA = False
		Pre_Bid()

	if statusB == 'traded':
		tradeB = tradedB - total_traded_bid 
		while True:	
			try:
				BI_balance_btc = bitstamp.fetch_balance()['BTC']['free']
				to_spend = tradeB * bitstamp.fetch_order_book(bitstamp.symbols[0])['asks'][0][0] 
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			break		
		if to_pend > BI_balance_btc:
			print ('No more BTC on Bitstamp')
			while True:	
				try:
					avai = round(round(BI_balance_btc / (float(bitstamp.fetch_order_book(bitstamp.symbols[0])['asks'][0][0])), 8) * 0.998 - 0.00000001, 8)
				except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
					continue
				break				
			Post_Market_Order_B(avai)
			exit()
		tradeB = round(tradeB * 1.008, 8)
		Post_Market_Order_B(tradeB)
		total_traded_bid = 0
		switchB = False
		Pre_Ask()

	if statusA == 'pending':
		while True:	
			try:
				priceA = bitstamp.fetch_order_book(bitstamp.symbols[0])['bids'][0][0]
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			break
		if priceA < best_priceA * (1 - (params / 2)) or priceA > best_priceA * (1 + (params / 2)):
			best_priceA = priceA
			Pre_Bid()
			reset = reset + 1
			print ('Ajusting order ', reset, 'times')

	if statusB == 'pending':
		while True:	
			try:
				priceB = bitstamp.fetch_order_book(bitstamp.symbols[0])['asks'][0][0]
			except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeError) as error:
				continue
			break
		if priceB > best_priceB * (1 + (params / 2)) or priceB < best_priceB * (1 - (params / 2)):
			best_priceB = priceB
			Pre_Ask()
			reset = reset + 1
			print ('Ajusting order ', reset, 'times')

	animation = "|/-\\"
	print(animation[idx % len(animation)], end="\r")
	idx += 1
	time.sleep(80)
