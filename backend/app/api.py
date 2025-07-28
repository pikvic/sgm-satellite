from fastapi import APIRouter
from pydantic import BaseModel
import pystac
import planetary_computer


# Declare models for API
# - SearchResult for Nominatim
# - SearchResult for STAC
# - SearchParams for STAC

# Declare routes
# - Nominatim search
# - stac search

# Make functions
# - nominatim search
# - stac search


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None



router = APIRouter(prefix="/api")


@router.get("/stac/", tags=["users"])
async def read_stac():
    item_url = "https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2/items/LC09_L2SP_114030_20250623_02_T1"

    # Load the individual item metadata and sign the assets
    item = pystac.Item.from_file(item_url)

    signed_item = planetary_computer.sign(item)
    
    # Open one of the data assets (other asset keys to use: 'red', 'blue', 'drad', 'emis', 'emsd', 'trad', 'urad', 'atran', 'cdist', 'green', 'nir08', 'lwir11', 'swir16', 'swir22', 'coastal', 'qa_pixel', 'qa_radsat', 'qa_aerosol')
    preview = signed_item.assets["rendered_preview"].href
    items = [{"name": key, "preview": preview, "href": value.href} for key, value in signed_item.assets.items() if ".TIF" in value.href]
    
    return items
