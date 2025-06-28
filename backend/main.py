import uvicorn
from extract import bitcoin_main
from fastapi import FastAPI, Query

app = FastAPI()
"""
Testing Steps
  uvicorn main:app --reload
  Go to http://127.0.0.1:8000/docs
"""

@app.get("/bitcoin_data")
def bitcoin_data():
    return bitcoin_main()
