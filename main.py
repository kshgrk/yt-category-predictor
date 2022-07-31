from fastapi import FastAPI
from fastapi import File, UploadFile
import pandas as pd
from io import StringIO
import os
import pandas as pd
import numpy as np
import re
from model import setup
import uvicorn

app = FastAPI()

@app.post("/upload_file")
async def create_upload_file(file: UploadFile = File(...)):
    if file.filename.endswith('.csv'):
        contents = await file.read()
        s = str(contents,'utf-8')
        data = StringIO(s)
        df = pd.read_csv(data)
        data.close()
        df.to_csv(file.filename)

    else:
         raise HTTPException( status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    return file.filename

@app.get("/model")
async def run_model():
    setup()
    return str("Done")

if __name__ == "__main__":
    uvicorn.run(
        app, host="127.0.0.1", port=8000, workers=1
    )
