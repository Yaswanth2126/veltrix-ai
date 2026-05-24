from SmartApi import SmartConnect
import pyotp
import pandas as pd
import time
from datetime import datetime

# =========================
# LOGIN
# =========================

API_KEY = "kD7uYjNd"
CLIENT_CODE = "Y60782760"
PASSWORD = "2109"
TOTP_SECRET = "MLEY4LTPD3BGEQ6AV3QWXJ6ZJQ"

obj = SmartConnect(api_key=API_KEY)

token = pyotp.TOTP(TOTP_SECRET).now()

data = obj.generateSession(CLIENT_CODE, PASSWORD, token)

# =========================
# STOCKS
# =========================

stocks = [

    {"symbol": "IRFC-EQ", "token": "14366"},

    {"symbol": "NHPC-EQ", "token": "17400"},

    {"symbol": "IDFCFIRSTB-EQ", "token": "11184"},

    {"symbol": "NBCC-EQ", "token": "31415"},

    {"symbol": "PNB-EQ", "token": "10666"},

    {"symbol": "CANBK-EQ", "token": "10794"},

    {"symbol": "BANKBARODA-EQ", "token": "4668"},

    {"symbol": "IOC-EQ", "token": "1624"}

]

exchange = "NSE"

# =========================
# SETTINGS
# =========================

quantity = 4

target_profit = 0.80

stoploss = 0.40

max_trades = 2

trade_count = 0

active_trade = False

daily_pnl = 0

# =========================
# STORAGE
# =========================

trade_data = {}

for stock in stocks:

    trade_data[stock["symbol"]] = {

        "prices": [],

        "in_trade": False,

        "buy_price": 0

    }

print("TOMORROW BOT STARTED")

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        current_time = datetime.now()

        current_hour = current_time.hour

        current_minute = current_time.minute

        print("\n========================")

        print("TIME:", current_time.strftime("%H:%M:%S"))

        print("TOTAL TRADES:", trade_count)

        print("DAILY PNL:", round(daily_pnl, 2))

        print("========================")

        # =========================
        # STOP AFTER 2:45 PM
        # =========================

        if current_hour == 14 and current_minute >= 45:

            print("NO NEW TRADES AFTER 2:45 PM")

            break

        if trade_count >= max_trades:

            print("MAX TRADES COMPLETED")

            break

        # =========================
        # FIND STRONGEST STOCK
        # =========================

        best_stock = None

        best_momentum = -999

        for stock in stocks:

            symbol = stock["symbol"]

            token_symbol = stock["token"]

            ltp = obj.ltpData(exchange, symbol, token_symbol)

            current_price = ltp["data"]["ltp"]

            prices = trade_data[symbol]["prices"]

            prices.append(current_price)

            if len(prices) > 20:

                prices.pop(0)

            print("\nSTOCK:", symbol)

            print("PRICE:", current_price)

            if len(prices) >= 10:

                df = pd.DataFrame(prices, columns=["price"])

                ema5 = df["price"].ewm(span=5).mean().iloc[-1]

                ema13 = df["price"].ewm(span=13).mean().iloc[-1]

                momentum = current_price - prices[-5]

                print("EMA5:", round(ema5, 2))

                print("EMA13:", round(ema13, 2))

                print("MOMENTUM:", round(momentum, 2))

                if ema5 > ema13 and momentum > best_momentum:

                    best_momentum = momentum

                    best_stock = {

                        "symbol": symbol,

                        "token": token_symbol,

                        "price": current_price

                    }

        # =========================
        # TRADE STRONGEST STOCK
        # =========================

        if best_stock and not active_trade:

            symbol = best_stock["symbol"]

            token_symbol = best_stock["token"]

            current_price = best_stock["price"]

            print("\n========================")

            print("STRONGEST STOCK:", symbol)

            print("========================")

            print("BUY SIGNAL GENERATED")

            orderparams = {

                "variety": "NORMAL",

                "tradingsymbol": symbol,

                "symboltoken": token_symbol,

                "transactiontype": "BUY",

                "exchange": exchange,

                "ordertype": "MARKET",

                "producttype": "INTRADAY",

                "duration": "DAY",

                "quantity": quantity

            }

            orderId = obj.placeOrder(orderparams)

            print("BUY ORDER:", orderId)

            trade_data[symbol]["buy_price"] = current_price

            trade_data[symbol]["in_trade"] = True

            active_trade = True

            trade_count += 1

            print("BUY PRICE:", current_price)

        # =========================
        # MANAGE ACTIVE TRADES
        # =========================

        for stock in stocks:

            symbol = stock["symbol"]

            token_symbol = stock["token"]

            if trade_data[symbol]["in_trade"]:

                ltp = obj.ltpData(exchange, symbol, token_symbol)

                current_price = ltp["data"]["ltp"]

                buy_price = trade_data[symbol]["buy_price"]

                pnl = round((current_price - buy_price) * quantity, 2)

                print("\nACTIVE TRADE:", symbol)

                print("LIVE PNL:", pnl)

                target_price = buy_price + target_profit

                stoploss_price = buy_price - stoploss

                # TARGET HIT

                if current_price >= target_price:

                    print("TARGET HIT")

                    sellparams = {

                        "variety": "NORMAL",

                        "tradingsymbol": symbol,

                        "symboltoken": token_symbol,

                        "transactiontype": "SELL",

                        "exchange": exchange,

                        "ordertype": "MARKET",

                        "producttype": "INTRADAY",

                        "duration": "DAY",

                        "quantity": quantity

                    }

                    sellOrder = obj.placeOrder(sellparams)

                    print("SELL ORDER:", sellOrder)

                    print("PROFIT BOOKED:", pnl)

                    daily_pnl += pnl

                    trade_data[symbol]["in_trade"] = False

                    active_trade = False

                # STOPLOSS HIT

                elif current_price <= stoploss_price:

                    print("STOPLOSS HIT")

                    sellparams = {

                        "variety": "NORMAL",

                        "tradingsymbol": symbol,

                        "symboltoken": token_symbol,

                        "transactiontype": "SELL",

                        "exchange": exchange,

                        "ordertype": "MARKET",

                        "producttype": "INTRADAY",

                        "duration": "DAY",

                        "quantity": quantity

                    }

                    sellOrder = obj.placeOrder(sellparams)

                    print("SELL ORDER:", sellOrder)

                    print("LOSS:", pnl)

                    daily_pnl += pnl

                    trade_data[symbol]["in_trade"] = False

                    active_trade = False

        time.sleep(5)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(5)