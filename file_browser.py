# file_browser.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve all files in current directory
app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")

@app.get("/file/{filename}")
def get_file(filename: str):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}