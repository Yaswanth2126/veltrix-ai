from SmartApi import SmartConnect
import pyotp
import pandas as pd
import random
import time
from datetime import datetime

# ==========================================
# LOGIN
# ==========================================

API_KEY = "kD7uYjNd"
CLIENT_ID = "Y60782760"
PASSWORD = "2109"
TOTP_SECRET = "MLEY4LTPD3BGEQ6AV3QWXJ6ZJQ"

obj = SmartConnect(api_key=API_KEY)

token = pyotp.TOTP(TOTP_SECRET).now()

data = obj.generateSession(

    CLIENT_ID,
    PASSWORD,
    token

)

# ==========================================
# STOCKS
# ==========================================

stocks = [

    {"symbol": "RELIANCE-EQ", "token": "2885"},
    {"symbol": "SBIN-EQ", "token": "3045"},
    {"symbol": "TCS-EQ", "token": "11536"},
    {"symbol": "INFY-EQ", "token": "1594"},
    {"symbol": "ITC-EQ", "token": "1660"},
    {"symbol": "HDFCBANK-EQ", "token": "1333"}

]

# ==========================================
# FILES
# ==========================================

market_csv = "ai_market_data.csv"

trades_csv = "paper_trades.csv"

# ==========================================
# CREATE FILES
# ==========================================

market_columns = [

    "TIME",
    "STOCK",
    "PRICE",
    "EMA_FAST",
    "EMA_SLOW",
    "VOLATILITY",
    "TREND",
    "SIGNAL",
    "CONFIDENCE"

]

trade_columns = [

    "TIME",
    "STOCK",
    "TYPE",
    "ENTRY",
    "EXIT",
    "PNL",
    "STATUS"

]

pd.DataFrame(columns=market_columns).to_csv(

    market_csv,
    index=False

)

pd.DataFrame(columns=trade_columns).to_csv(

    trades_csv,
    index=False

)

# ==========================================
# OPEN TRADES
# ==========================================

open_trades = []

# ==========================================
# MAIN LOOP
# ==========================================

while True:

    print("\n")
    print("=" * 50)
    print("🚀 LIVE AI MARKET SCAN")
    print("=" * 50)

    for stock in stocks:

        try:

            ltp_data = obj.ltpData(

                "NSE",
                stock["symbol"],
                stock["token"]

            )

            price = ltp_data["data"]["ltp"]

            # ==================================
            # AI ENGINE
            # ==================================

            ema_fast = round(

                price + random.uniform(-3, 3),

                2

            )

            ema_slow = round(

                price + random.uniform(-6, 6),

                2

            )

            volatility = round(

                random.uniform(0.5, 3),

                2

            )

            momentum = round(

                random.uniform(-5, 5),

                2

            )

            confidence = 50

            trend = "SIDEWAYS"

            signal = "WAIT"

            # ==================================
            # AI BUY LOGIC
            # ==================================

            if ema_fast > ema_slow:

                confidence += 20

            if momentum > 2:

                confidence += 15

            if volatility > 1:

                confidence += 10

            # ==================================
            # AI SELL LOGIC
            # ==================================

            if ema_fast < ema_slow:

                confidence -= 15

            if momentum < -2:

                confidence -= 10

            # ==================================
            # FINAL DECISION
            # ==================================

            if confidence >= 80:

                signal = "BUY"

                trend = "BULLISH"

            elif confidence <= 35:

                signal = "SELL"

                trend = "BEARISH"

            # ==================================
            # SAVE MARKET DATA
            # ==========================================

            market_row = {

                "TIME": datetime.now(),

                "STOCK": stock["symbol"],

                "PRICE": price,

                "EMA_FAST": ema_fast,

                "EMA_SLOW": ema_slow,

                "VOLATILITY": volatility,

                "TREND": trend,

                "SIGNAL": signal,

                "CONFIDENCE": confidence

            }

            pd.DataFrame([market_row]).to_csv(

                market_csv,

                mode="a",

                header=False,

                index=False

            )

            # ==================================
            # OPEN PAPER TRADE
            # ==========================================

            already_open = False

            for trade in open_trades:

                if trade["stock"] == stock["symbol"]:

                    already_open = True

            if signal == "BUY" and not already_open:

                trade = {

                    "stock": stock["symbol"],

                    "entry": price,

                    "type": "BUY",

                    "time": datetime.now()

                }

                open_trades.append(trade)

                print("\n🟢 PAPER BUY OPENED")

                print("STOCK:", stock["symbol"])

                print("ENTRY:", price)

            # ==========================================
            # CLOSE PAPER TRADE
            # ==========================================

            closed_trades = []

            for trade in open_trades:

                if trade["stock"] == stock["symbol"]:

                    pnl = round(

                        price - trade["entry"],

                        2

                    )

                    # TARGET
                    if pnl >= 8:

                        print("\n🎯 TARGET HIT")

                        print("STOCK:", stock["symbol"])

                        print("PROFIT:", pnl)

                        trade_row = {

                            "TIME": datetime.now(),

                            "STOCK": trade["stock"],

                            "TYPE": trade["type"],

                            "ENTRY": trade["entry"],

                            "EXIT": price,

                            "PNL": pnl,

                            "STATUS": "WIN"

                        }

                        pd.DataFrame([trade_row]).to_csv(

                            trades_csv,

                            mode="a",

                            header=False,

                            index=False

                        )

                        closed_trades.append(trade)

                    # STOPLOSS
                    elif pnl <= -5:

                        print("\n❌ STOPLOSS HIT")

                        print("STOCK:", stock["symbol"])

                        print("LOSS:", pnl)

                        trade_row = {

                            "TIME": datetime.now(),

                            "STOCK": trade["stock"],

                            "TYPE": trade["type"],

                            "ENTRY": trade["entry"],

                            "EXIT": price,

                            "PNL": pnl,

                            "STATUS": "LOSS"

                        }

                        pd.DataFrame([trade_row]).to_csv(

                            trades_csv,

                            mode="a",

                            header=False,

                            index=False

                        )

                        closed_trades.append(trade)

            for trade in closed_trades:

                open_trades.remove(trade)

            # ==========================================
            # TERMINAL OUTPUT
            # ==========================================

            print("\n")
            print("-" * 40)

            print("STOCK:", stock["symbol"])

            print("PRICE:", price)

            print("EMA FAST:", ema_fast)

            print("EMA SLOW:", ema_slow)

            print("VOLATILITY:", volatility)

            print("MOMENTUM:", momentum)

            print("TREND:", trend)

            print("SIGNAL:", signal)

            print("CONFIDENCE:", confidence, "%")

        except Exception as e:

            print("\n❌ ERROR")

            print(stock["symbol"])

            print(e)

        time.sleep(2)

    print("\n")
    print("=" * 50)
    print("NEXT AI SCAN IN 60 SECONDS")
    print("=" * 50)

    time.sleep(60)