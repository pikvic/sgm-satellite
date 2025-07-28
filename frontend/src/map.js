import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import { ScaleLine, defaults as defaultControls } from 'ol/control';
import { fromLonLat } from 'ol/proj';
import GeoJSON from 'ol/format/GeoJSON';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';

import ImageLayer from 'ol/layer/Image';
import ImageStatic from 'ol/source/ImageStatic';
import { Projection } from 'ol/proj';
import { getCenter } from 'ol/extent';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';

// Инициализация карты
export function initMap(target) {

    const scaleControl = new ScaleLine({
      units: 'metric',
      bar: true,
      steps: 4,
      text: true,
      minWidth: 140,
    });


    const map = new Map({
        target: target,
        layers: [
            new TileLayer({
                source: new OSM(),
                title: 'Базовая карта'
            })
        ],
        view: new View({
            center: fromLonLat([37.6178, 55.7517]), // Москва
            zoom: 8,
            projection: "EPSG:3857"
        }),
        controls: defaultControls().extend([scaleControl])
    });
    return map;
}

// Добавление нового слоя
export function addLayer(map, source, title, style) {
    map.addLayer(layer);
    return layer;
}

// Виджет масштаба
export function updateScaleWidget(map) {
    const scaleWidget = document.getElementById('scale-widget');
    const scale = map.getView().getScale();
    const resolution = map.getView().getResolution();
    const units = map.getView().getProjection().getUnits();
    
    // Конвертация в километры
    let scaleInKm = 'N/A';
    if (units === 'm') {
        scaleInKm = (resolution * scale * 100).toFixed(2) + ' км';
    }
    
    scaleWidget.textContent = `Масштаб: 1:${Math.round(scale)} | ${scaleInKm}`;
}

// Стиль для точек из CSV
export function createPointStyle(feature) {
    return new Style({
        image: new CircleStyle({
            radius: 5 + feature.get('value') / 10,
            fill: new Fill({
                color: `rgba(63, 127, 191, 0.7)`
            }),
            stroke: new Stroke({
                color: 'white',
                width: 1
            })
        })
    });
}


// Добавление изображения на карту
export function addImageLayer(map, url, extent, projection) {
  const proj = new Projection({ code: projection });
  
  const layer = new ImageLayer({
    source: new ImageStatic({
      url: url,
      projection: proj,
      imageExtent: extent
    }),
    title: 'Загруженное изображение'
  });
  
  map.addLayer(layer);
  map.getView().fit(extent);
  return layer;
}

// Добавление CSV данных
export function addCSVLayer(map, data, lonField, latField, sizeField, colorField) {
  const features = [];
  
  data.forEach(row => {
    const lon = parseFloat(row[lonField]);
    const lat = parseFloat(row[latField]);
    
    if (!isNaN(lon) && !isNaN(lat)) {
      const feature = new Feature({
        geometry: new Point(fromLonLat([lon, lat])),
        ...row
      });
      
      features.push(feature);
    }
  });
  
  const source = new VectorSource({ features });
  
  // Стиль в зависимости от данных
  const styleFunction = (feature) => {
    const size = sizeField ? parseFloat(feature.get(sizeField)) || 5 : 5;
    const color = colorField ? feature.get(colorField) || '#3388ff' : '#3388ff';
    
    return new Style({
      image: new CircleStyle({
        radius: size,
        fill: new Fill({ color }),
        stroke: new Stroke({ color: '#fff', width: 1 })
      })
    });
  };
  
  const layer = new VectorLayer({
    source: source,
    style: styleFunction,
    title: 'CSV данные'
  });
  
  map.addLayer(layer);
  return layer;
}

// Инструмент для рисования прямоугольника
export function setupDrawInteraction(map, callback) {
  const source = new VectorSource();
  const layer = new VectorLayer({ source });
  map.addLayer(layer);
  
  const draw = new Draw({
    source: source,
    type: 'Circle',
    geometryFunction: createBox()
  });
  
  map.addInteraction(draw);
  
  draw.on('drawend', (event) => {
    const geometry = event.feature.getGeometry();
    const extent = geometry.getExtent();
    const bbox = transformExtent(extent, 'EPSG:3857', 'EPSG:4326');
    
    // Убираем временный слой
    map.removeInteraction(draw);
    map.removeLayer(layer);
    
    callback(bbox);
  });
  
  return draw;
}