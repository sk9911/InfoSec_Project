from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/home", response_class=HTMLResponse)
async def read(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/student", response_class=HTMLResponse)
async def read(request: Request):
    return templates.TemplateResponse("student.html", {"request": request})

@app.get("/professor", response_class=HTMLResponse)
async def read(request: Request):
    return templates.TemplateResponse("prof.html", {"request": request})

@app.get("/doctor", response_class=HTMLResponse)
async def read(request: Request):
    return templates.TemplateResponse("doc.html", {"request": request})
