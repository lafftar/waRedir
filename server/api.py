import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from utils.root import get_project_root

TEMPLATES = Jinja2Templates(directory=f"{get_project_root()}/server/static/html")

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=f'{get_project_root()}/server/static'),
    name="static",
)

@app.get("/")
async def root(request: Request):
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request},
    )


@app.get('/favicon.ico')
async def favicon():
    return FileResponse(f'{get_project_root()}/server/static/ico/favicon.ico')


if __name__ == "__main__":
    uvicorn.run('api:app', host='localhost', port=1338, reload=True)