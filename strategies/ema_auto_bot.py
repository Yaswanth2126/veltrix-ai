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
# STOCK DETAILS
# =========================

symbol = "YESBANK-EQ"
token_symbol = "11915"
exchange = "NSE"

# =========================
# VARIABLES
# =========================

prices = []

last_signal = None

quantity = 1

print("EMA AUTO BOT STARTED")

# =========================
# LOOP
# =========================

while True:

    try:

        ltp = obj.ltpData(exchange, symbol, token_symbol)

        current_price = ltp["data"]["ltp"]

        print("LIVE PRICE:", current_price)

        prices.append(current_price)

        # Keep only latest 20 prices
        if len(prices) > 20:
            prices.pop(0)

        # Need minimum 10 prices
        if len(prices) >= 10:

            df = pd.DataFrame(prices, columns=["price"])

            ema5 = df["price"].ewm(span=5).mean().iloc[-1]

            ema10 = df["price"].ewm(span=10).mean().iloc[-1]

            print("EMA5:", round(ema5, 2))
            print("EMA10:", round(ema10, 2))

            # =========================
            # BUY SIGNAL
            # =========================

            if ema5 > ema10 and last_signal != "BUY":

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

                last_signal = "BUY"

            # =========================
            # SELL SIGNAL
            # =========================

            elif ema5 < ema10 and last_signal != "SELL":

                print("SELL SIGNAL GENERATED")

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

                last_signal = "SELL"

        time.sleep(5)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(5)