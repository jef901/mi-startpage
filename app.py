from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
app = FastAPI()
@app.get("/", response_class=HTMLResponse)
def root():
    return "<h1>mi-startpage</h1><p>En desarrollo.</p>"
