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
# MIDCAP STOCKS
# =========================

stocks = [
    {"symbol": "RVNL-EQ", "token": "9552"},
    {"symbol": "IRFC-EQ", "token": "14366"},
    {"symbol": "NHPC-EQ", "token": "17400"},
    {"symbol": "IDFCFIRSTB-EQ", "token": "11184"},
    {"symbol": "SAIL-EQ", "token": "2963"},
]

exchange = "NSE"

# =========================
# SETTINGS
# =========================

quantity = 1

target_profit = 1.0

stoploss = 0.50

daily_target = 40

daily_loss_limit = -15

cooldown_seconds = 300

# =========================
# STORAGE
# =========================

stock_data = {}

daily_pnl = 0

for stock in stocks:

    stock_data[stock["symbol"]] = {
        "prices": [],
        "in_trade": False,
        "buy_price": 0,
        "last_trade_time": 0
    }

print("MONDAY STRATEGY BOT STARTED")

# =========================
# RSI FUNCTION
# =========================

def calculate_rsi(prices, period=14):

    df = pd.DataFrame(prices, columns=["price"])

    delta = df["price"].diff()

    gain = delta.where(delta > 0, 0)

    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()

    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        print("\n==============================")
        print("DAILY PNL:", round(daily_pnl, 2))
        print("==============================")

        # DAILY TARGET STOP
        if daily_pnl >= daily_target:

            print("DAILY TARGET REACHED")

            break

        # DAILY LOSS STOP
        if daily_pnl <= daily_loss_limit:

            print("DAILY LOSS LIMIT HIT")

            break

        for stock in stocks:

            symbol = stock["symbol"]

            token_symbol = stock["token"]

            ltp = obj.ltpData(exchange, symbol, token_symbol)

            current_price = ltp["data"]["ltp"]

            print("\n----------------------")
            print("STOCK:", symbol)
            print("LIVE PRICE:", current_price)

            prices = stock_data[symbol]["prices"]

            prices.append(current_price)

            if len(prices) > 50:
                prices.pop(0)

            # NEED DATA
            if len(prices) >= 20:

                df = pd.DataFrame(prices, columns=["price"])

                ema3 = df["price"].ewm(span=3).mean().iloc[-1]

                ema8 = df["price"].ewm(span=8).mean().iloc[-1]

                rsi = calculate_rsi(prices)

                print("EMA3:", round(ema3, 2))
                print("EMA8:", round(ema8, 2))
                print("RSI:", round(rsi, 2))

                in_trade = stock_data[symbol]["in_trade"]

                buy_price = stock_data[symbol]["buy_price"]

                last_trade_time = stock_data[symbol]["last_trade_time"]

                current_time = time.time()

                # COOLDOWN
                if current_time - last_trade_time < cooldown_seconds:

                    print("Cooldown Active")

                    continue

                # =========================
                # BUY ENTRY
                # =========================

                if ema3 > ema8 and rsi > 55 and not in_trade:

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

                    # TARGET HIT
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

                        daily_pnl += pnl

                    # STOPLOSS HIT
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

                        daily_pnl += pnl

        time.sleep(5)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(5)