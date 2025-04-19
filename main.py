from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/cotacao/{ticker}")
def get_cotacao(ticker: str):
    try:
        ticker = ticker.upper()
        acao = yf.Ticker(ticker)
        info = acao.info

        preco = info.get("regularMarketPrice")
        nome = info.get("shortName")
        moeda = info.get("currency")

        # Histórico dos últimos 5 dias
        historico = acao.history(period="5d")
        hist_list = []
        if not historico.empty:
            for data, linha in historico.iterrows():
                hist_list.append({
                    "data": data.strftime("%Y-%m-%d"),
                    "preco": round(linha["Close"], 2)
                })

        # Proventos (últimos 5)
        dividendos = acao.dividends
        prov_list = []
        if not dividendos.empty:
            ultimos = dividendos.tail(5)
            for data, valor in ultimos.items():
                prov_list.append({
                    "data": data.strftime("%Y-%m-%d"),
                    "valor": round(float(valor), 2)
                })

        return {
            "ticker": ticker,
            "preco": preco,
            "nome": nome,
            "moeda": moeda,
            "historico": hist_list,
            "proventos": prov_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
