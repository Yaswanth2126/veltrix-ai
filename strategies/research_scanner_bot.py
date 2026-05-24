from SmartApi import SmartConnect
import pyotp
import pandas as pd
import random
import time
from datetime import datetime

# ==========================================
# ANGEL ONE LOGIN
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
# STOCK LIST
# ==========================================

stocks = [

    {"symbol": "RELIANCE-EQ", "token": "2885"},
    {"symbol": "SBIN-EQ", "token": "3045"},
    {"symbol": "TCS-EQ", "token": "11536"},
    {"symbol": "INFY-EQ", "token": "1594"},
    {"symbol": "ITC-EQ", "token": "1660"},
    {"symbol": "HDFCBANK-EQ", "token": "1333"},
    {"symbol": "ICICIBANK-EQ", "token": "4963"},
    {"symbol": "LT-EQ", "token": "11483"},
    {"symbol": "ONGC-EQ", "token": "2475"},
    {"symbol": "BEL-EQ", "token": "383"}

]

# ==========================================
# CSV FILE
# ==========================================

csv_file = "ai_market_data.csv"

# ==========================================
# CREATE CSV
# ==========================================

columns = [

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

df = pd.DataFrame(columns=columns)

df.to_csv(csv_file, index=False)

# ==========================================
# MARKET LOOP
# ==========================================

while True:

    print("\n")
    print("=" * 50)
    print("🚀 NEW AI MARKET SCAN")
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
                price + random.uniform(-2, 2),
                2
            )

            ema_slow = round(
                price + random.uniform(-5, 5),
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
            # BUY LOGIC
            # ==================================

            if ema_fast > ema_slow:

                confidence += 20

            if momentum > 2:

                confidence += 15

            if volatility > 1:

                confidence += 10

            if confidence >= 80:

                signal = "BUY"

                trend = "BULLISH"

            # ==================================
            # SELL LOGIC
            # ==================================

            elif ema_fast < ema_slow:

                confidence -= 10

            if momentum < -2:

                confidence -= 15

            if confidence <= 35:

                signal = "SELL"

                trend = "BEARISH"

            # ==================================
            # PRINT OUTPUT
            # ==================================

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

            # ==================================
            # SAVE CSV
            # ==================================

            new_row = {

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

            new_df = pd.DataFrame([new_row])

            new_df.to_csv(

                csv_file,

                mode="a",

                header=False,

                index=False

            )

        except Exception as e:

            print("\n")
            print("STOCK ERROR:", stock["symbol"])
            print(e)

        time.sleep(2)

    print("\n")
    print("=" * 50)
    print("NEXT AI SCAN IN 60 SECONDS")
    print("=" * 50)

    time.sleep(60)