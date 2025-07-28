import './style.css';
import Map from 'ol/Map.js';
import OSM from 'ol/source/OSM.js';
import TileLayer from 'ol/layer/Tile.js';
import View from 'ol/View.js';

function initMap(div) {

    const map = new Map({
        target: 'map',
        layers: [
            new TileLayer({
            source: new OSM(),
            }),
        ],
        view: new View({
            center: [0, 0],
            zoom: 2,
        }),
    });

    return map;
}


// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    // Инициализация карты
    const map = initMap('map');
    
    // Инициализация UI
    // setupUI(map);
    
    // Добавить после инициализации карты
    // map.on('addlayer', () => updateLayerList(map));
    // map.on('removelayer', () => updateLayerList(map));

    // Обновление виджета масштаба при движении карты
    // map.on('moveend', () => {
    //     updateScaleWidget(map);
    // });
    
    // Логирование начального действия
    logAction('Приложение инициализировано');
});