// Заглушка для поиска местоположений
export function searchLocation(query) {
    console.log(`API: Поиск местоположения "${query}"`);

    return new Promise((resolve, reject) => {
          fetch(`https://nominatim.openstreetmap.org/search?q=${query}&format=geojson&limit=10&accept-language=ru-RU&polygon_geojson=1`)
              .then(res => res.json())
              .then(data => resolve(data))
              .catch(err => reject(err));
    });

   
}

// Заглушка для поиска спутниковых снимков
export function searchSatelliteImagery(bbox, date, satellite, limit = 5) {
  console.log(`API: Поиск снимков ${satellite} за ${date} в bbox: ${bbox}`);
  return new Promise((resolve, reject) => {
        fetch(`http://127.0.0.1:8001/api/stac`)
            .then(res => res.json())
            .then(data => resolve(data))
            .catch(err => reject(err));
  });
}

// Заглушка для добавления COG слоя
export function addCogLayer(collectionId, itemId) {
  /*
  Реальный запрос:
  return axios.post('/api/map/add-cog', { collectionId, itemId });
  */
  
  return Promise.resolve({
    status: 'success',
    layerId: `cog-${Date.now()}`
  });
}