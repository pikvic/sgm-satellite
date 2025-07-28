import { searchLocation, searchSatelliteImagery } from './api.js';
import { addLayer, createPointStyle } from './map.js';
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import GeoJSON from 'ol/format/GeoJSON';
import { Modal } from 'bootstrap';
import { setupDrawInteraction } from './map.js';
import Papa from 'papaparse';
import { Style, Stroke, Fill } from 'ol/style.js';
import { GeoTIFF } from 'ol/source.js';
import TileLayer from 'ol/layer/Tile.js';

// Настройка обработчиков UI
export function setupUI(map) {
    // Поиск по тексту
    document.getElementById('search-btn').addEventListener('click', () => {
        const query = document.getElementById('search-input').value;
        if (!query) return;
        console.log("clicked");
        searchLocation(query).then(results => {
            console.log(results);
            displaySearchResults(map, results);
            logAction(`Выполнен поиск: "${query}"`);
        });
    });
    
    // Поиск спутниковых снимков
    document.getElementById('satellite-search-btn').addEventListener('click', () => {
        // Заглушка - в реальности здесь будет диалог выбора региона
        const bbox = [30, 50, 40, 60]; // Пример bbox
        const date = '2023-01-01';
        const satellite = 'sentinel-2';
        
        searchSatelliteImagery(bbox, date, satellite).then(images => {
            displaySatelliteResults(map, images);
            logAction(`Поиск снимков: ${satellite} за ${date}`);
        });
    });
    
    // Обработчики других кнопок...
    // Обработчики для модальных окон
  const imageModal = new Modal(document.getElementById('image-modal'));
  const csvModal = new Modal(document.getElementById('csv-modal'));
  
  // Открытие модальных окон
  document.getElementById('add-image-btn').addEventListener('click', () => imageModal.show());
  document.getElementById('add-csv-btn').addEventListener('click', () => csvModal.show());
  
  // Добавление изображения
  document.getElementById('confirm-image').addEventListener('click', () => {
    const fileInput = document.getElementById('image-file');
    const projection = document.getElementById('image-projection').value;
    const extentStr = document.getElementById('image-extent').value;
    
    if (!fileInput.files.length || !extentStr) return;
    
    const file = fileInput.files[0];
    const extent = extentStr.split(',').map(Number);
    const url = URL.createObjectURL(file);
    
    addImageLayer(map, url, extent, projection);
    logAction(`Добавлено изображение: ${file.name}`);
    imageModal.hide();
  });
  
  // Добавление CSV
  document.getElementById('confirm-csv').addEventListener('click', () => {
    const fileInput = document.getElementById('csv-file');
    const lonField = document.getElementById('lon-column').value;
    const latField = document.getElementById('lat-column').value;
    const sizeField = document.getElementById('size-column').value;
    const colorField = document.getElementById('color-column').value;
    
    if (!fileInput.files.length || !lonField || !latField) return;
    
    const file = fileInput.files[0];
    Papa.parse(file, {
      header: true,
      complete: (results) => {
        addCSVLayer(map, results.data, lonField, latField, sizeField, colorField);
        logAction(`Добавлен CSV файл: ${file.name} с ${results.data.length} записями`);
        csvModal.hide();
      }
    });
  });
  
  // Инструмент для выбора региона
  document.getElementById('satellite-search-btn').addEventListener('click', () => {
    logAction('Начало выбора региона для поиска снимков');
    
    setupDrawInteraction(map, (bbox) => {
      const date = prompt('Введите дату (ГГГГ-ММ-ДД):', '2023-01-01');
      const satellite = prompt('Выберите спутник:', 'sentinel-2');
      
      if (date && satellite) {
        searchSatelliteImagery(bbox, date, satellite).then(images => {
          displaySatelliteResults(images);
          logAction(`Поиск снимков: ${satellite} за ${date} в регионе ${bbox}`);
        });
      }
    });
  });
}

// Отображение результатов поиска
function displaySearchResults(map, results) {
    const container = document.getElementById('search-results');
    container.innerHTML = '';
    
    const style = new Style({
      stroke: new Stroke({
        color: 'blue',
        width: 3,
      }),
      fill: new Fill({
        color: 'rgba(0, 0, 255, 0.1)',
      }),
    });

    results.features.forEach(result => {
        const card = document.createElement('div');
        card.className = 'card card-layer mb-2';
        card.innerHTML = `
            <div class="card-body">
                <h6>${result.properties.name}</h6>
                <p>Тип: ${result.type}</p>
                <button class="btn btn-sm btn-outline-primary add-layer-btn">Добавить</button>
            </div>
        `;
        
        card.querySelector('.add-layer-btn').addEventListener('click', () => {
            const vectorLayer = new VectorLayer({
              source: new VectorSource({
                projection: "EPSG:3857",
                features: new GeoJSON().readFeatures(results),
                style: style
              })
            });
            map.addLayer(vectorLayer);
            map.render();
            console.log(map.getLayers());
            logAction(`Добавлен слой: ${result.properties.name}`);
        });
        
        container.appendChild(card);
    });
}

// Отображение результатов поиска снимков
function displaySatelliteResults(map, images) {
  const container = document.getElementById('search-results');
  container.innerHTML = '<h5 class="mt-2">Результаты поиска снимков</h5>';
  
  images.forEach(img => {
    const card = document.createElement('div');
    card.className = 'card card-layer mb-2';
    card.innerHTML = `
      <div class="card-body">
        <h6>${img.name}</h6>
        <img src="${img.preview}" class="img-thumbnail mb-2">
        <button class="btn btn-sm btn-outline-primary add-image-btn">Добавить слой</button>
      </div>
    `;
    
    card.querySelector('.add-image-btn').addEventListener('click', () => {
      // В реальности здесь будет запрос к бэкенду для получения COG URL
      const source = new GeoTIFF({
        sources: [
          {
            url: img.href,
          },
        ],
      });
      map.addLayer( 
        new TileLayer({
          source: source,
        })
      );
      map.render();
      logAction(`Добавлен слой снимка: ${img.name}`);
      
    });
    
    container.appendChild(card);
  });
}

// Панель управления слоями
export function updateLayerList(map) {
    const container = document.getElementById('layer-list');
    container.innerHTML = '';
    
    map.getLayers().forEach(layer => {
        if (layer.get('title')) {
            const layerItem = document.createElement('div');
            layerItem.className = 'd-flex justify-content-between align-items-center mb-2';
            layerItem.innerHTML = `
                <div>
                    <input type="checkbox" checked class="layer-visibility me-2">
                    ${layer.get('title')}
                </div>
                <button class="btn btn-sm btn-danger"><i class="bi bi-trash"></i></button>
            `;
            
            // Управление видимостью
            const checkbox = layerItem.querySelector('.layer-visibility');
            checkbox.checked = layer.getVisible();
            checkbox.addEventListener('change', () => {
                layer.setVisible(checkbox.checked);
                logAction(`${checkbox.checked ? 'Включен' : 'Отключен'} слой: ${layer.get('title')}`);
            });
            
            // Удаление слоя
            layerItem.querySelector('button').addEventListener('click', () => {
                map.removeLayer(layer);
                updateLayerList(map);
                logAction(`Удален слой: ${layer.get('title')}`);
            });
            
            container.appendChild(layerItem);
        }
    });
}

// Логирование действий
export function logAction(message) {
    const logContainer = document.getElementById('action-log');
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `<small>[${new Date().toLocaleTimeString()}]</small> ${message}`;
    logContainer.prepend(entry);
    
    // Ограничение количества записей
    if (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.lastChild);
    }
}