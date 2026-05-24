from SmartApi import SmartConnect
import pyotp
import pandas as pd
import time

# LOGIN DETAILS
API_KEY = "kD7uYjNd"
CLIENT_CODE = "Y60782760"
PASSWORD = "2109"
TOTP_SECRET = "MLEY4LTPD3BGEQ6AV3QWXJ6ZJQ"

# CONNECT
obj = SmartConnect(api_key=API_KEY)

token = pyotp.TOTP(TOTP_SECRET).now()

data = obj.generateSession(CLIENT_CODE, PASSWORD, token)

# STOCK
symbol = "YESBANK-EQ"
token_symbol = "11915"
exchange = "NSE"

# SETTINGS
quantity = 1

prices = []

bought = False

print("EMA BOT STARTED")

while True:

    # GET LIVE PRICE
    ltp = obj.ltpData(exchange, symbol, token_symbol)

    current_price = ltp["data"]["ltp"]

    print("LIVE PRICE:", current_price)

    # STORE PRICES
    prices.append(current_price)

    # KEEP ONLY LAST 20
    if len(prices) > 20:
        prices.pop(0)

    # NEED MINIMUM DATA
    if len(prices) >= 10:

        df = pd.DataFrame(prices, columns=["price"])

        # EMA 5
        ema5 = df["price"].ewm(span=5).mean().iloc[-1]

        # EMA 10
        ema10 = df["price"].ewm(span=10).mean().iloc[-1]

        print("EMA5:", round(ema5, 2))
        print("EMA10:", round(ema10, 2))

        # BUY CONDITION
        if ema5 > ema10 and bought == False:

            print("BUY SIGNAL GENERATED")

            buy_order = obj.placeOrder({
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": token_symbol,
                "transactiontype": "BUY",
                "exchange": exchange,
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": quantity
            })

            print("BUY ORDER:", buy_order)

            bought = True

        # SELL CONDITION
        elif ema5 < ema10 and bought == True:

            print("SELL SIGNAL GENERATED")

            sell_order = obj.placeOrder({
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": token_symbol,
                "transactiontype": "SELL",
                "exchange": exchange,
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": quantity
            })

            print("SELL ORDER:", sell_order)

            bought = False

    time.sleep(5)