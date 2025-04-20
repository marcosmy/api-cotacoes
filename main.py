from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import datetime

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
        # Valor de 1 ano atrás
        hoje = datetime.datetime.now()
        um_ano_atras = hoje - datetime.timedelta(days=365)
        hist_ano = acao.history(start=um_ano_atras.strftime("%Y-%m-%d"), end=hoje.strftime("%Y-%m-%d"))
        data_ano = valor_ano = None
        if not hist_ano.empty:
            primeira_linha = hist_ano.iloc[0]
            data_ano = hist_ano.index[0].strftime("%Y-%m-%d")
            valor_ano = round(primeira_linha["Close"], 2)
        
        return {
            "ticker": ticker,
            "preco": preco,
            "nome": nome,
            "moeda": moeda,
            "historico": hist_list,
            "proventos": prov_list,
            "ano_atras": {
                "data_ano": data_ano,
                "valor_ano": valor_ano
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
