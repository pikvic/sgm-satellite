from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from .stac import search_microsoft, search_roscosmos
from .api import router

from fastapi.middleware.cors import CORSMiddleware

COLLECTIONS = [
    {
        "name": "landsat-c2-l2",
        "description": "Landsat Collection 2 Level-2 Science Products, consisting of atmospherically corrected surface reflectance and surface temperature image data. Collection 2 Level-2 Science Products are available from August 22, 1982 to present. This dataset represents the global archive of Level-2 data from Landsat Collection 2 acquired by the Thematic Mapper onboard Landsat 4 and 5, the Enhanced Thematic Mapper onboard Landsat 7, and the Operatational Land Imager and Thermal Infrared Sensor onboard Landsat 8 and 9. Images are stored in cloud-optimized GeoTIFF format.",
        "source": "Microsoft Planetary Computer",
        "provider": "NASA, USGS",
        "search": search_microsoft
    },
    {
        "name": "modis-09A1-061",
        "description": "The Moderate Resolution Imaging Spectroradiometer (MODIS) 09A1 Version 6.1 product provides an estimate of the surface spectral reflectance of MODIS Bands 1 through 7 corrected for atmospheric conditions such as gasses, aerosols, and Rayleigh scattering. Along with the seven 500 meter (m) reflectance bands are two quality layers and four observation bands. For each pixel, a value is selected from all the acquisitions within the 8-day composite period. The criteria for the pixel choice include cloud and solar zenith. When several acquisitions meet the criteria the pixel with the minimum channel 3 (blue) value is used.",
        "source": "Microsoft Planetary Computer",
        "provider": "NASA LP DAAC at the USGS EROS Center",
        "search": search_microsoft
    },
    {
        "name": "roscosmos-opendata.MM",
        "description": "Глобальные мозайки. Солнечно-синхронная метеорологическая космическая система Метеор-М. По состоянию на 2025 год состоит из двух космических аппаратов. Радиометр МСУ-МР производит непрерывное сканирование.",
        "source": "Роскосмос",
        "provider": "Роскосмос",
        "search": search_roscosmos
    },
    
]


app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/collections", response_class=HTMLResponse)
async def collections(request: Request):

    return templates.TemplateResponse(request=request, name="collections.html", context={"collections": COLLECTIONS})

@app.get("/collections/{name}", response_class=HTMLResponse)
async def collection(name, request: Request):
    collection = [col for col in COLLECTIONS if col["name"] == name][0]
    return templates.TemplateResponse(request=request, name="collection.html", context={"collection": collection})

@app.post("/collections/{name}/results", response_class=HTMLResponse)
async def search(
    name: str, 
    start: Annotated[str, Form()], 
    end: Annotated[str, Form()], 
    lat1: Annotated[str, Form()], 
    lat2: Annotated[str, Form()], 
    lon1: Annotated[str, Form()],
    lon2: Annotated[str, Form()],
    request: Request
):
    bbox = [lon1, lat1, lon2, lat2]
    time_range = f"{start}/{end}"
    collection = [col for col in COLLECTIONS if col["name"] == name][0]
    results = collection["search"](name, bbox=bbox, time_range=time_range)
    return templates.TemplateResponse(request=request, name="results.html", context={"name": name, "results": results})

