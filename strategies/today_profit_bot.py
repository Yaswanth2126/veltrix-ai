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

    {"symbol": "IOC-EQ", "token": "1624"},

    {"symbol": "PNB-EQ", "token": "10666"},

    {"symbol": "CANBK-EQ", "token": "10794"},

    {"symbol": "BANKBARODA-EQ", "token": "4668"},

    {"symbol": "NBCC-EQ", "token": "31415"}

]

exchange = "NSE"

# =========================
# SETTINGS
# =========================

quantity = 3

target_profit = 1.20

stoploss = 0.60

# total entries allowed in full day
max_new_entries = 6

# simultaneous active trades
max_active_trades = 2

daily_target = 60

daily_loss_limit = -25

new_entries = 0

daily_pnl = 0

active_trades = 0

# =========================
# STORAGE
# =========================

trade_data = {}

for stock in stocks:

    trade_data[stock["symbol"]] = {

        "prices": [],

        "in_trade": False,

        "buy_price": 0,

        "highest_price": 0

    }

print("MULTI POSITION PROFIT BOT STARTED")

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        current_time = datetime.now()

        hour = current_time.hour

        minute = current_time.minute

        print("\n========================")

        print("TIME:", current_time.strftime("%H:%M:%S"))

        print("NEW ENTRIES:", new_entries)

        print("ACTIVE TRADES:", active_trades)

        print("DAILY PNL:", round(daily_pnl, 2))

        print("========================")

        # =========================
        # MARKET CLOSE EXIT
        # =========================

        if hour == 15 and minute >= 10:

            print("MARKET CLOSE EXIT")

            for stock in stocks:

                symbol = stock["symbol"]

                token_symbol = stock["token"]

                if trade_data[symbol]["in_trade"]:

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

                    print("FORCE SELL:", sellOrder)

            break

        # =========================
        # DAILY TARGET / LOSS
        # =========================

        if daily_pnl >= daily_target:

            print("DAILY TARGET REACHED")

            break

        if daily_pnl <= daily_loss_limit:

            print("DAILY LOSS LIMIT HIT")

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
        # NEW BUY ENTRY
        # =========================

        if (

            best_stock

            and active_trades < max_active_trades

            and new_entries < max_new_entries

        ):

            symbol = best_stock["symbol"]

            token_symbol = best_stock["token"]

            current_price = best_stock["price"]

            # avoid duplicate entries
            if not trade_data[symbol]["in_trade"]:

                print("\n========================")

                print("BUY SIGNAL:", symbol)

                print("========================")

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

                trade_data[symbol]["highest_price"] = current_price

                trade_data[symbol]["in_trade"] = True

                active_trades += 1

                new_entries += 1

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

                highest_price = trade_data[symbol]["highest_price"]

                if current_price > highest_price:

                    trade_data[symbol]["highest_price"] = current_price

                    highest_price = current_price

                pnl = round(

                    (current_price - buy_price) * quantity,

                    2

                )

                print("\nACTIVE TRADE:", symbol)

                print("BUY PRICE:", buy_price)

                print("CURRENT PRICE:", current_price)

                print("LIVE PNL:", pnl)

                # =========================
                # TARGET HIT
                # =========================

                if current_price >= buy_price + target_profit:

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

                    print("PROFIT:", pnl)

                    daily_pnl += pnl

                    trade_data[symbol]["in_trade"] = False

                    active_trades -= 1

                # =========================
                # STOPLOSS HIT
                # =========================

                elif current_price <= buy_price - stoploss:

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

                    active_trades -= 1

        time.sleep(5)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(5)