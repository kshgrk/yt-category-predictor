from fastapi import File, UploadFile
import pandas as pd
from io import StringIO
import os
import pandas as pd
import numpy as np
import re
from model import setup
import uvicorn
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi import HTTPException, FastAPI, Response, Depends
from uuid import UUID, uuid4
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

class SessionData(BaseModel):
    username: str


cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)
backend = InMemoryBackend[UUID, SessionData]()


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)

app = FastAPI()

@app.post("/create_session/{name}")
async def create_session(name: str, response: Response):

    session = uuid4()
    data = SessionData(username=name)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {name}"


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data


@app.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"


@app.post("/upload_file")
async def create_upload_file(response: Response, session_id: UUID = Depends(cookie), file: UploadFile = File(...)):
    path = os.path.join("./", str(session_id))
    if os.path.exists(path) == False:
        os.mkdir(path)
    if file.filename.endswith('.csv'):
        contents = await file.read()
        s = str(contents,'utf-8')
        data = StringIO(s)
        df = pd.read_csv(data)
        data.close()
        data_path = os.path.join(path, file.filename)
        df.to_csv(data_path)

    else:
         raise HTTPException( status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    return file.filename

@app.get("/model")
async def run_model(response: Response, session_id: UUID = Depends(cookie)):
    path = os.path.join("./", str(session_id))
    setup()
    sb = pd.read_csv(path, 'submission.csv')
    return FileResponse(path+'submission.csv')

if __name__ == "__main__":
    uvicorn.run(
        app, host="127.0.0.1", port=8000, workers=1
    )
