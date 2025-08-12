from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routes.flight_routes import router as flight_router
from routes.weather_routes import router as weather_router
from routes.sightseeing_area_routes import router as sightseeing_area_router
from routes.hotel_routes import router as hotel_router
from fastapi.staticfiles import StaticFiles 

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(flight_router, prefix="/flights")
app.include_router(weather_router, prefix="/weather")
app.include_router(sightseeing_area_router, prefix="/sightseeing-areas")
app.include_router(hotel_router, prefix="/hotel")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})