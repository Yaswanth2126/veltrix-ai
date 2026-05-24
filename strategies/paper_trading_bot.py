from SmartApi import SmartConnect
import pyotp
import pandas as pd
import time
from datetime import datetime
import csv
import os

# =====================================
# LOGIN
# =====================================

API_KEY = "kD7uYjNd"
CLIENT_CODE = "Y60782760"
PASSWORD = "2109"
TOTP_SECRET = "MLEY4LTPD3BGEQ6AV3QWXJ6ZJQ"

obj = SmartConnect(api_key=API_KEY)

token = pyotp.TOTP(TOTP_SECRET).now()

data = obj.generateSession(
    CLIENT_CODE,
    PASSWORD,
    token
)

# =====================================
# PAPER TRADING MODE
# =====================================

PAPER_TRADING = True

# =====================================
# STOCKS
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
# SETTINGS
# =====================================

quantity = 1

EMA_FAST = 9
EMA_SLOW = 21

STOPLOSS_PERCENT = 0.7
TARGET_PERCENT = 1.5

TRAILING_STOPLOSS = 0.4

MAX_TRADES_PER_DAY = 5
MAX_DAILY_LOSS = 100

COOLDOWN_SECONDS = 900

MIN_EMA_GAP = 0.05

# =====================================
# CSV FILE
# =====================================

csv_file = "trade_history.csv"

if not os.path.exists(csv_file):

    with open(csv_file, mode="w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([

            "TIME",

            "STOCK",

            "ENTRY",

            "EXIT",

            "P/L",

            "EXIT_REASON"

        ])

# =====================================
# STORAGE
# =====================================

prices = {}

positions = {}

last_signal = {}

last_trade_time = {}

daily_pnl = 0

trade_count = 0

# =====================================
# INITIALIZE
# =====================================

for stock in stocks:

    symbol = stock["symbol"]

    prices[symbol] = []

    last_signal[symbol] = None

    last_trade_time[symbol] = 0

    positions[symbol] = {

        "position_open": False,

        "entry_price": 0,

        "highest_price": 0

    }

# =====================================
# START
# =====================================

print("\n==============================")
print("SAFE PAPER TRADING BOT STARTED")
print("==============================")

# =====================================
# MAIN LOOP
# =====================================

while True:

    try:

        # =============================
        # DAILY LIMIT CHECK
        # =============================

        if daily_pnl <= -MAX_DAILY_LOSS:

            print("\nMAX DAILY LOSS HIT")

            break

        if trade_count >= MAX_TRADES_PER_DAY:

            print("\nMAX TRADES LIMIT HIT")

            break

        # =============================
        # LOOP STOCKS
        # =============================

        for stock in stocks:

            symbol = stock["symbol"]

            token_symbol = stock["token"]

            print("\n======================")
            print("STOCK:", symbol)

            # =========================
            # LIVE PRICE
            # =========================

            ltp = obj.ltpData(
                exchange,
                symbol,
                token_symbol
            )

            current_price = float(
                ltp["data"]["ltp"]
            )

            print("LIVE PRICE:", current_price)

            prices[symbol].append(
                current_price
            )

            # Keep latest 100 prices
            if len(prices[symbol]) > 100:

                prices[symbol].pop(0)

            # Need enough prices
            if len(prices[symbol]) < 30:

                print("COLLECTING DATA...")

                continue

            # =========================
            # DATAFRAME
            # =========================

            df = pd.DataFrame(
                prices[symbol],
                columns=["price"]
            )

            # =========================
            # EMA
            # =========================

            ema_fast = df["price"].ewm(
                span=EMA_FAST
            ).mean().iloc[-1]

            ema_slow = df["price"].ewm(
                span=EMA_SLOW
            ).mean().iloc[-1]

            ema_gap = abs(
                ema_fast - ema_slow
            )

            print("EMA FAST:", round(ema_fast, 2))
            print("EMA SLOW:", round(ema_slow, 2))
            print("EMA GAP:", round(ema_gap, 3))

            # =========================
            # FILTERS
            # =========================

            candle_bullish = (

                current_price

                > df["price"].iloc[-2]

            )

            volume_confirmed = True

            market_bullish = (

                ema_fast > ema_slow

            )

            higher_tf_confirmed = (

                ema_fast > ema_slow

            )

            # =========================
            # POSITION DATA
            # =========================

            position_open = positions[symbol]["position_open"]

            entry_price = positions[symbol]["entry_price"]

            current_time = time.time()

            # =========================
            # BUY CONDITIONS
            # =========================

            buy_condition = (

                ema_fast > ema_slow

                and ema_gap > MIN_EMA_GAP

                and candle_bullish

                and volume_confirmed

                and market_bullish

                and higher_tf_confirmed

                and not position_open

                and last_signal[symbol] != "BUY"

                and (

                    current_time

                    - last_trade_time[symbol]

                    > COOLDOWN_SECONDS
                )

            )

            # =========================
            # PAPER BUY
            # =========================

            if buy_condition:

                print("\nPAPER BUY EXECUTED")

                positions[symbol]["position_open"] = True

                positions[symbol]["entry_price"] = current_price

                positions[symbol]["highest_price"] = current_price

                last_signal[symbol] = "BUY"

                last_trade_time[symbol] = current_time

                trade_count += 1

                print("ENTRY PRICE:", current_price)

            # =========================
            # POSITION MANAGEMENT
            # =========================

            if positions[symbol]["position_open"]:

                entry_price = positions[symbol]["entry_price"]

                highest_price = positions[symbol]["highest_price"]

                # Update trailing high
                if current_price > highest_price:

                    positions[symbol]["highest_price"] = current_price

                    highest_price = current_price

                pnl = (

                    current_price - entry_price

                ) * quantity

                print("P/L:", round(pnl, 2))

                target_price = (

                    entry_price

                    * (

                        1 + TARGET_PERCENT / 100
                    )
                )

                stoploss_price = (

                    entry_price

                    * (

                        1 - STOPLOSS_PERCENT / 100
                    )
                )

                trailing_stop = (

                    highest_price

                    * (

                        1 - TRAILING_STOPLOSS / 100
                    )
                )

                print("TARGET:", round(target_price, 2))

                print("STOPLOSS:", round(stoploss_price, 2))

                print("TRAILING:", round(trailing_stop, 2))

                exit_trade = False

                exit_reason = ""

                # =====================
                # EXIT CONDITIONS
                # =====================

                if current_price <= stoploss_price:

                    print("STOPLOSS HIT")

                    exit_trade = True

                    exit_reason = "STOPLOSS"

                elif current_price >= target_price:

                    print("TARGET HIT")

                    exit_trade = True

                    exit_reason = "TARGET"

                elif current_price <= trailing_stop:

                    print("TRAILING STOPLOSS HIT")

                    exit_trade = True

                    exit_reason = "TRAILING STOPLOSS"

                elif ema_fast < ema_slow:

                    print("EMA REVERSAL EXIT")

                    exit_trade = True

                    exit_reason = "EMA REVERSAL"

                # =====================
                # PAPER SELL
                # =====================

                if exit_trade:

                    print("PAPER SELL EXECUTED")

                    # SAVE TRADE DATA
                    with open(csv_file, mode="a", newline="") as file:

                        writer = csv.writer(file)

                        writer.writerow([

                            datetime.now(),

                            symbol,

                            round(entry_price, 2),

                            round(current_price, 2),

                            round(pnl, 2),

                            exit_reason

                        ])

                    daily_pnl += pnl

                    print("TRADE P/L:", round(pnl, 2))

                    print("DAILY P/L:", round(daily_pnl, 2))

                    positions[symbol]["position_open"] = False

                    positions[symbol]["entry_price"] = 0

                    positions[symbol]["highest_price"] = 0

                    last_signal[symbol] = "SELL"

                    last_trade_time[symbol] = current_time

        # =============================
        # WAIT
        # =============================

        time.sleep(10)

    except Exception as e:

        print("\nERROR:", e)

        time.sleep(10)