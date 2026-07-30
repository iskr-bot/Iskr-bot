import requests
import pandas as pd
import numpy as np

# Configuración Telegram
TOKEN = "8494446929:AAEFkzadLUcHneji7eQ4IAAdR9nzkJgElGU"
CHAT_ID = "-1004364441063"
THREAD_ID = 124

# Configuración Binance
SYMBOL = "BTCUSDT"
INTERVAL = "15m"

def obtener_velas(symbol, interval, limit=250):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        res = requests.get(url, timeout=10).json()
        df = pd.DataFrame(res, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print(f"[ERROR BINANCE] {e}")
        return None

def calcular_emas(df):
    periodos = [5, 9, 20, 50, 90, 200]
    for p in periodos:
        df[f'EMA_{p}'] = df['close'].ewm(span=p, adjust=False).mean()
    return df

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "message_thread_id": THREAD_ID,
        "text": mensaje,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[ERROR TELEGRAM] {e}")
        return False

def analizar_mercado():
    df = obtener_velas(SYMBOL, INTERVAL)
    if df is None or df.empty:
        return
    
    df = calcular_emas(df)
    last = df.iloc[-1]
    price = last['close']
    
    # Condición Matriz EMA
    ema5 = last['EMA_5']
    ema9 = last['EMA_9']
    ema20 = last['EMA_20']
    ema50 = last['EMA_50']
    ema90 = last['EMA_90']
    ema200 = last['EMA_200']
    
    tendencia = "DESCONOCIDA"
    if ema5 > ema9 > ema20 > ema50 > ema90 > ema200:
        tendencia = "ALCISTA FUERTE 🚀"
    elif ema5 < ema9 < ema20 < ema50 < ema90 < ema200:
        tendencia = "BAJISTA FUERTE 🔻"
    else:
        tendencia = "EN COMPRESIÓN / CONSOLIDACIÓN ⚠️"

    mensaje = (
        f"⚡ <b>ISKR ENGINE - ANÁLISIS DE MERCADO</b>\n\n"
        f"<b>Par:</b> {SYMBOL} ({INTERVAL})\n"
        f"<b>Precio Actual:</b> ${price:,.2f}\n"
        f"<b>Estructura Matriz EMA:</b> {tendencia}\n\n"
        f"🔹 <b>EMA 5:</b> ${ema5:,.2f}\n"
        f"🔹 <b>EMA 200:</b> ${ema200:,.2f}\n\n"
        f"<i>Estado: Monitoreo automático en vivo (Nube).</i>"
    )
    
    if enviar_telegram(mensaje):
        print("[ISKR ENGINE] Análisis enviado con éxito al canal de Señales.")

if __name__ == "__main__":
    analizar_mercado()
