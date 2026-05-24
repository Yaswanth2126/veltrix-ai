from SmartApi import SmartConnect
import pyotp
import pandas as pd
import time

# =====================================
# LOGIN DETAILS
# =====================================

API_KEY = "kD7uYjNd"
CLIENT_CODE = "Y60782760"
PASSWORD = "2109"
TOTP_SECRET = "MLEY4LTPD3BGEQ6AV3QWXJ6ZJQ"

# =====================================
# CONNECT TO ANGEL ONE
# =====================================

obj = SmartConnect(api_key=API_KEY)

token = pyotp.TOTP(TOTP_SECRET).now()

data = obj.generateSession(
    CLIENT_CODE,
    PASSWORD,
    token
)

# =====================================
# STOCK LIST
# =====================================

stocks = [

    {
        "symbol": "YESBANK-EQ",
        "token": "11915"
    },

    {
        "symbol": "IRFC-EQ",
        "token": "11809"
    },

    {
        "symbol": "NBCC-EQ",
        "token": "31415"
    }

]

exchange = "NSE"

# =====================================
# SAFE SETTINGS
# =====================================

quantity = 1

EMA_FAST = 9
EMA_SLOW = 21

STOPLOSS_PERCENT = 0.7
TARGET_PERCENT = 1.5

MAX_TRADES_PER_DAY = 3
MAX_DAILY_LOSS = 100

COOLDOWN_SECONDS = 300

# =====================================
# STORAGE VARIABLES
# =====================================

prices = {}

positions = {}

trade_count = 0

daily_pnl = 0

last_trade_time = 0

# =====================================
# INITIALIZE STORAGE
# =====================================

for stock in stocks:

    prices[stock["symbol"]] = []

    positions[stock["symbol"]] = {

        "position_open": False,

        "entry_price": 0

    }

# =====================================
# START
# =====================================

print("SAFE MULTI STOCK EMA BOT STARTED")

# =====================================
# MAIN LOOP
# =====================================

while True:

    try:

        # ==============================
        # DAILY SAFETY CHECK
        # ==============================

        if daily_pnl <= -MAX_DAILY_LOSS:

            print("MAX DAILY LOSS HIT")

            break

        if trade_count >= MAX_TRADES_PER_DAY:

            print("MAX TRADES LIMIT REACHED")

            break

        # ==============================
        # LOOP THROUGH STOCKS
        # ==============================

        for stock in stocks:

            symbol = stock["symbol"]

            token_symbol = stock["token"]

            print("\n========================")
            print("STOCK:", symbol)

            # ==========================
            # GET LIVE PRICE
            # ==========================

            ltp = obj.ltpData(
                exchange,
                symbol,
                token_symbol
            )

            current_price = float(
                ltp["data"]["ltp"]
            )

            print("LIVE PRICE:", current_price)

            prices[symbol].append(current_price)

            # Keep latest 50 prices
            if len(prices[symbol]) > 50:

                prices[symbol].pop(0)

            # Wait for enough data
            if len(prices[symbol]) < 25:

                print("COLLECTING DATA...")

                continue

            # ==========================
            # EMA CALCULATION
            # ==========================

            df = pd.DataFrame(
                prices[symbol],
                columns=["price"]
            )

            ema_fast = df["price"].ewm(
                span=EMA_FAST
            ).mean().iloc[-1]

            ema_slow = df["price"].ewm(
                span=EMA_SLOW
            ).mean().iloc[-1]

            print("EMA FAST:", round(ema_fast, 2))

            print("EMA SLOW:", round(ema_slow, 2))

            current_time = time.time()

            # ==========================
            # POSITION DATA
            # ==========================

            position_open = positions[symbol]["position_open"]

            entry_price = positions[symbol]["entry_price"]

            # ==========================
            # BUY CONDITION
            # ==========================

            if (

                ema_fast > ema_slow

                and not position_open

                and (

                    current_time - last_trade_time

                    > COOLDOWN_SECONDS
                )

            ):

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

                    "price": "0",

                    "squareoff": "0",

                    "stoploss": "0",

                    "quantity": quantity
                }

                orderid = obj.placeOrder(
                    orderparams
                )

                print("BUY ORDER:", orderid)

                positions[symbol]["position_open"] = True

                positions[symbol]["entry_price"] = current_price

                trade_count += 1

                last_trade_time = current_time

            # ==========================
            # POSITION MANAGEMENT
            # ==========================

            if positions[symbol]["position_open"]:

                entry_price = positions[symbol]["entry_price"]

                pnl = (

                    current_price - entry_price

                ) * quantity

                print("P/L:", round(pnl, 2))

                stoploss_price = (

                    entry_price

                    * (

                        1 - STOPLOSS_PERCENT / 100
                    )
                )

                target_price = (

                    entry_price

                    * (

                        1 + TARGET_PERCENT / 100
                    )
                )

                print(

                    "TARGET:",

                    round(target_price, 2)
                )

                print(

                    "STOPLOSS:",

                    round(stoploss_price, 2)
                )

                exit_trade = False

                # ======================
                # STOPLOSS
                # ======================

                if current_price <= stoploss_price:

                    print("STOPLOSS HIT")

                    exit_trade = True

                # ======================
                # TARGET
                # ======================

                elif current_price >= target_price:

                    print("TARGET HIT")

                    exit_trade = True

                # ======================
                # EMA SELL
                # ======================

                elif ema_fast < ema_slow:

                    print("EMA SELL SIGNAL")

                    exit_trade = True

                # ======================
                # SELL ORDER
                # ======================

                if exit_trade:

                    sellparams = {

                        "variety": "NORMAL",

                        "tradingsymbol": symbol,

                        "symboltoken": token_symbol,

                        "transactiontype": "SELL",

                        "exchange": exchange,

                        "ordertype": "MARKET",

                        "producttype": "INTRADAY",

                        "duration": "DAY",

                        "price": "0",

                        "squareoff": "0",

                        "stoploss": "0",

                        "quantity": quantity
                    }

                    sellorder = obj.placeOrder(
                        sellparams
                    )

                    print("SELL ORDER:", sellorder)

                    daily_pnl += pnl

                    print(

                        "DAILY PNL:",

                        round(daily_pnl, 2)
                    )

                    positions[symbol]["position_open"] = False

                    positions[symbol]["entry_price"] = 0

                    last_trade_time = current_time

        time.sleep(5)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(5)