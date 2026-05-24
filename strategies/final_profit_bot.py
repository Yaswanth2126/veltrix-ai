from SmartApi import SmartConnect
import pyotp
import pandas as pd
import time

# =========================
# LOGIN DETAILS
# =========================

API_KEY = "kD7uYjNd"
CLIENT_CODE = "Y60782760"
PASSWORD = "2109"
TOTP_SECRET = "MLEY4LTPD3BGEQ6AV3QWXJ6ZJQ"

# =========================
# CONNECT
# =========================

obj = SmartConnect(api_key=API_KEY)

token = pyotp.TOTP(TOTP_SECRET).now()

data = obj.generateSession(CLIENT_CODE, PASSWORD, token)

# =========================
# STOCKS UNDER ₹100
# =========================

stocks = [
    {"symbol": "YESBANK-EQ", "token": "11915"},
    {"symbol": "IRFC-EQ", "token": "14366"},
    {"symbol": "SUZLON-EQ", "token": "12018"},
    {"symbol": "UCOBANK-EQ", "token": "11253"},
    {"symbol": "SOUTHBANK-EQ", "token": "5948"},
]

exchange = "NSE"

# =========================
# SETTINGS
# =========================

quantity = 1

target_profit = 0.50

stoploss = 0.25

cooldown_seconds = 120

# =========================
# STORAGE
# =========================

stock_data = {}

for stock in stocks:

    stock_data[stock["symbol"]] = {
        "prices": [],
        "in_trade": False,
        "buy_price": 0,
        "last_trade_time": 0
    }

print("FINAL PROFIT BOT STARTED")

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        for stock in stocks:

            symbol = stock["symbol"]

            token_symbol = stock["token"]

            # =========================
            # LIVE PRICE
            # =========================

            ltp = obj.ltpData(exchange, symbol, token_symbol)

            current_price = ltp["data"]["ltp"]

            print("\n======================")
            print("STOCK:", symbol)
            print("LIVE PRICE:", current_price)

            prices = stock_data[symbol]["prices"]

            prices.append(current_price)

            if len(prices) > 30:
                prices.pop(0)

            # =========================
            # NEED DATA
            # =========================

            if len(prices) >= 15:

                df = pd.DataFrame(prices, columns=["price"])

                ema3 = df["price"].ewm(span=3).mean().iloc[-1]

                ema8 = df["price"].ewm(span=8).mean().iloc[-1]

                print("EMA3:", round(ema3, 2))
                print("EMA8:", round(ema8, 2))

                in_trade = stock_data[symbol]["in_trade"]

                buy_price = stock_data[symbol]["buy_price"]

                last_trade_time = stock_data[symbol]["last_trade_time"]

                current_time = time.time()

                # =========================
                # COOLDOWN
                # =========================

                if current_time - last_trade_time < cooldown_seconds:
                    print("Cooldown Active")
                    continue

                # =========================
                # BUY ENTRY
                # =========================

                if ema3 > ema8 and not in_trade:

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

                    stock_data[symbol]["buy_price"] = current_price

                    stock_data[symbol]["in_trade"] = True

                    stock_data[symbol]["last_trade_time"] = current_time

                    print("BUY PRICE:", current_price)

                # =========================
                # TRADE MANAGEMENT
                # =========================

                if stock_data[symbol]["in_trade"]:

                    buy_price = stock_data[symbol]["buy_price"]

                    pnl = round(current_price - buy_price, 2)

                    print("P/L:", pnl)

                    target_price = buy_price + target_profit

                    stoploss_price = buy_price - stoploss

                    print("TARGET:", round(target_price, 2))
                    print("STOPLOSS:", round(stoploss_price, 2))

                    # =========================
                    # TARGET HIT
                    # =========================

                    if current_price >= target_price:

                        print("TARGET HIT")

                        orderparams = {
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

                        orderId = obj.placeOrder(orderparams)

                        print("SELL ORDER:", orderId)

                        stock_data[symbol]["in_trade"] = False

                        stock_data[symbol]["last_trade_time"] = current_time

                    # =========================
                    # STOPLOSS HIT
                    # =========================

                    elif current_price <= stoploss_price:

                        print("STOPLOSS HIT")

                        orderparams = {
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

                        orderId = obj.placeOrder(orderparams)

                        print("SELL ORDER:", orderId)

                        stock_data[symbol]["in_trade"] = False

                        stock_data[symbol]["last_trade_time"] = current_time

        time.sleep(5)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(5)