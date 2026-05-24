from SmartApi import SmartConnect
import pyotp
import time

# LOGIN DETAILS
API_KEY = "kD7uYjNd"
CLIENT_CODE = "Y60782760"
PASSWORD = "2109"
TOTP_SECRET = "MLEY4LTPD3BGEQ6AV3QWXJ6ZJQ"

# CONNECT TO ANGEL ONE
obj = SmartConnect(api_key=API_KEY)

# GENERATE TOTP
token = pyotp.TOTP(TOTP_SECRET).now()

# LOGIN SESSION
data = obj.generateSession(CLIENT_CODE, PASSWORD, token)

# STOCK DETAILS
symbol = "YESBANK-EQ"
token_symbol = "11915"
exchange = "NSE"

# SETTINGS
quantity = 1
target_profit = 0.20
stop_loss = 0.20

# GET CURRENT PRICE
ltp = obj.ltpData(exchange, symbol, token_symbol)

buy_price = ltp["data"]["ltp"]

print("BUY PRICE:", buy_price)

# PLACE BUY ORDER
buy_order = obj.placeOrder({
    "variety": "NORMAL",
    "tradingsymbol": symbol,
    "symboltoken": token_symbol,
    "transactiontype": "BUY",
    "exchange": exchange,
    "ordertype": "MARKET",
    "producttype": "INTRADAY",
    "duration": "DAY",
    "quantity": quantity
})

print("BUY ORDER PLACED:", buy_order)

# TARGET & STOPLOSS
target_price = buy_price + target_profit
stop_price = buy_price - stop_loss

print("TARGET PRICE:", target_price)
print("STOPLOSS PRICE:", stop_price)

# LIVE MONITORING
while True:

    ltp = obj.ltpData(exchange, symbol, token_symbol)

    current_price = ltp["data"]["ltp"]

    profit = current_price - buy_price

    print(
        "LIVE:",
        current_price,
        "| P/L:",
        round(profit, 2)
    )

    # TARGET HIT
    if current_price >= target_price:

        sell_order = obj.placeOrder({
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token_symbol,
            "transactiontype": "SELL",
            "exchange": exchange,
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": quantity
        })

        print("TARGET HIT")
        print("SELL ORDER PLACED:", sell_order)

        break

    # STOPLOSS HIT
    elif current_price <= stop_price:

        sell_order = obj.placeOrder({
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token_symbol,
            "transactiontype": "SELL",
            "exchange": exchange,
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": quantity
        })

        print("STOPLOSS HIT")
        print("SELL ORDER PLACED:", sell_order)

        break

    time.sleep(5)