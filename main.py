from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routes.flight_routes import router as flight_router
from routes.weather_routes import router as weather_router
# from routes.hotel_routes import router as hotel_router

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.include_router(flight_router, prefix="/flights")
app.include_router(weather_router, prefix="/weather")
# app.include_router(hotel_router, prefix="/hotels")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})