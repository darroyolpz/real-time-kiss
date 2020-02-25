from functions_file import *
# https://pypi.org/project/schedule/
import schedule, warnings, json, requests, time, decimal
from decimal import getcontext, Decimal
import numpy as np
from discord import Webhook, RequestsWebhookAdapter
from statistics import mean 
warnings.simplefilter(action = "ignore", category = RuntimeWarning)

# Webhook settings
url_wb = os.environ.get('DISCORD_WH')
webhook = Webhook.from_url(url_wb, adapter=RequestsWebhookAdapter())

'''
# Set the coins you want to retrieve
coins = ['BTC', 'ADA', 'ALGO', 'ANKR', 'ARPA', 'ATOM', 'BAND', 'BAT', 'BCH', 'BEAM', 'BNB',
		'BTT', 'CELR', 'CHZ', 'COCOS', 'COS', 'CVC', 'DASH', 'DENT', 'DOCK', 'DOGE', 'DUSK',
		'ENJ', 'EOS', 'ERD', 'ETC', 'ETH', 'FET', 'FUN', 'GTO', 'HBAR', 'HC', 'HOT', 'ICX',
		'IOST', 'IOTA', 'KAVA', 'KEY', 'LINK', 'LTC', 'MATIC', 'MLT', 'NANO', 'NEO', 'NPXS',
		'NULS', 'ONG', 'OMG', 'ONE', 'ONT', 'QTUM', 'PERL', 'REN', 'RVN', 'THETA', 'TOMO',
		'TRX', 'VET', 'WAN', 'WAVES', 'XLM', 'XMR', 'XTZ', 'ZEC', 'ZIL', 'ZRX']
'''

# Set the coins you want to retrieve
coins = ['BTC', 'LTC', 'ADA', 'ETH', 'LTC', 'BAT', 'BCH', 'BNB', 'EOS', 'THETA', 'ALGO',
		'ETC', 'ATOM', 'FET', 'ICX', 'LINK', 'MATIC', 'NEO','ONE', 'TRX', 'XTZ']

# Get the previous days closes ------------------------------------------------
def previous_days_closes(coin):
	# Check execution time
	start_time = time.time()

	# Create dataframe
	df = coin_data_function(coin, start=datetime.now() + timedelta(days = -120),
									end = datetime.now(), tf='1D')
	df['Coin'] = coin

	# Drop useless columns
	cols = ['Open', 'High', 'Low', 'Volume', 'USD volume', 'Number of trades',
			'Buy volume', 'USD buy volume']

	df.drop(cols, axis=1, inplace=True)

	# Stop running time
	print(coin)
	print("--- %s seconds ---" % (time.time() - start_time))
	print('\n')

	return df

# Getting alert on MAs values -------------------------------------------------
def sma_alert(coin, close_values):
	currentDT = datetime.now()
	print('SMA_alert checking', coin)
	print (str(currentDT))
	print('\n')

	# Get actual price of the coin
	price = actual_price(coin)

	# Get the significant figures
	d = decimal.Decimal(str(price))
	fig = -d.as_tuple().exponent + 1

	# Get the MAs
	mas = [25, 99]
	sma_vals = sma_value(coin, close_values, mas, price)

	# Sensibility factor
	sens_factor = 1+(0.05/100) # 0.05%
	
	for ma, sma in zip(mas, sma_vals):
		max_sma = sma*sens_factor
		if (price > sma) & (price < max_sma):
			# Discord message
			sl = round(price*(1-0.033),fig)
			target = round(price*(1+0.066),fig)
			opt_entry = round((price+sl)/2,fig)

			webhook.send(f":fire: {coin} kiss on daily SMA{ma}\nCurrent price: {price}\nOptimal entry: {opt_entry}\nSL: {sl}\n:dart: Target: {target}\n")

			# Console log
			currentDT = datetime.now()
			print (str(currentDT)) 
			print(f"{coin} kiss on daily SMA{ma} \nCurrent price: {price}")
			print('\n')

# Get the job done ------------------------------------------------------------
# Once a day, just at the beginning of the day
def you_only_had_one_job(coins=coins):
	# Empty dataframe for future coin closes
	cols = ['Open time', 'Close', 'Coin']
	df_closes = pd.DataFrame(columns = cols)

	# Loop
	for coin in coins:
		df_coin = previous_days_closes(coin)
		df_closes = df_closes.append(df_coin)
		name ='Coins closes data.xlsx'
		df_closes.to_excel(name, index =  False)

# Every fucking second --------------------------------------------------------
def every_fucking_second(coins=coins):
	excel_file = 'Coins closes data.xlsx'
	df_closes = pd.read_excel(excel_file)

	for coin in coins:
		close_values = df_closes.loc[df_closes['Coin'] == coin, 'Close'].to_numpy()
		sma_alert(coin, close_values)

# Start it just in case nobody is going to be hurt
you_only_had_one_job() 

# Schedule tasks
schedule.every().day.at("01:01").do(you_only_had_one_job)
schedule.every(15).seconds.do(every_fucking_second)

while True:
	schedule.run_pending()