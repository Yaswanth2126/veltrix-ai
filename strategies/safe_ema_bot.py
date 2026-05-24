from SmartApi import SmartConnect
import pyotp
import pandas as pd
import time

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
# LOW PRICE STOCKS
# =========================

stocks = [
    {"symbol": "YESBANK-EQ", "token": "11915"},
    {"symbol": "IRFC-EQ", "token": "14366"},
    {"symbol": "SUZLON-EQ", "token": "12018"},
    {"symbol": "PNB-EQ", "token": "10666"},
]

exchange = "NSE"

# =========================
# SETTINGS
# =========================

quantity = 1

target_profit = 0.20

stoploss = 0.10

# =========================
# STORAGE
# =========================

stock_data = {}

for stock in stocks:

    stock_data[stock["symbol"]] = {
        "prices": [],
        "in_trade": False,
        "buy_price": 0,
        "last_signal": None
    }

print("MULTI STOCK SAFE EMA BOT STARTED")

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

            # Keep latest 20 prices only
            if len(prices) > 20:
                prices.pop(0)

            # =========================
            # EMA CALCULATION
            # =========================

            if len(prices) >= 10:

                df = pd.DataFrame(prices, columns=["price"])

                ema5 = df["price"].ewm(span=2).mean().iloc[-1]

                ema10 = df["price"].ewm(span=4).mean().iloc[-1]

                print("EMA5:", round(ema5, 2))
                print("EMA10:", round(ema10, 2))

                in_trade = stock_data[symbol]["in_trade"]

                # =========================
                # BUY SIGNAL
                # =========================

                if ema5 > ema10 and not in_trade:

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

                    stock_data[symbol]["last_signal"] = "BUY"

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

        time.sleep(5)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(5)