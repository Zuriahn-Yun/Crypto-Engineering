import uvicorn
from extract import bitcoin_main
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/bitcoin_data")
def bitcoin_data():
    return bitcoin_main()
