import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import FileResponse, RedirectResponse
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

@app.get("/wa")
async def root(request: Request):
    return TEMPLATES.TemplateResponse(
        "wa.html",
        {"request": request},
    )


@app.get('/redirect/{url}')
async def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url)


@app.get('/favicon.ico')
async def favicon():
    return FileResponse(f'{get_project_root()}/server/static/ico/favicon.ico')


if __name__ == "__main__":
    uvicorn.run('api:app', host='0.0.0.0', port=1338, reload=True)