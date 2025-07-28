import pystac_client
import planetary_computer

def search_microsoft(collection, bbox, time_range):
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    search = catalog.search(collections=[collection], bbox=bbox, datetime=time_range)
    items = search.item_collection()
    result = []
    for item in items:
        data = {
            "id": item.id,
            "url": [a.href for a in item.assets.values() if a.media_type == "image/png"][0]
        }
        result.append(data)
    return result

def search_roscosmos(collection, bbox, time_range):
    catalog = pystac_client.Client.open(
        "https://api.gptl.ru/stac/api/v1"
    )
    search = catalog.search(collections=[collection], bbox=bbox, datetime=time_range)
    items = search.item_collection()
    result = []
    for item in items:
        data = {
            "id": item.id,
            "url": [a.href for a in item.assets.values() if a.media_type == "image/png"][0]
        }
        result.append(data)
    return result

