import app.config as config
from time import sleep
import httpx
import datetime
from bs4 import BeautifulSoup
from app.sml import get_projmapper, readproj2
import rasterio
from rasterio.transform import Affine
from pyproj import Transformer, CRS
from rasterio.warp import calculate_default_transform, reproject, Resampling
import zipfile
from app.schema import NoaaRegionEnum
from httpx._exceptions import RemoteProtocolError
import random

def clear_files_for_job(job_id):
    # path = config.UPLOAD_DIR / job_id
    # if path.exists():
    #     for f in path.iterdir():
    #         f.unlink()
    #     path.rmdir()
    path = config.DOWNLOAD_DIR / job_id
    if path.exists():
        for f in path.iterdir():
            f.unlink()
        path.rmdir()

def get_or_create_dir(root, job_id):
    path = root / job_id
    if not path.exists():
        path.mkdir()
    return path

def generate_filename(path, prefix, name):
    return path / f'{prefix}_{name}'

def error(message):
    return {'success': False, 'error': message}

def success():
    return {'success': True}

def ready(results):
    return {'ready': True, 'results': results}

def validate_noaa_params(params):
    # if 'columns' in params:
    #     res = parse_columns(params['columns'], ncolumns)
    #     if not res['success']:
    #         return res
    # if 'columns1' in params:
    #     res = parse_columns(params['columns1'], ncolumns)
    #     if not res['success']:
    #         return res
    # if 'columns2' in params:
    #     res = parse_columns(params['columns2'], ncolumns)
    #     if not res['success']:
    #         return res
    # if 'target_column' in params:
    #     if params['target_column'] > ncolumns:
    #         return {'success': False, 'error': 'Указанный номер столбца больше, чем есть во входном файле'}
    return {'success': True}

def dsystem_info(task_id):
    headers = {"Content-Type": "application/json"}
    command = f'[ "info", "{task_id}" ]'
    response = httpx.post(config.URL_DSYSTEM, headers=headers, content=command, auth=config.AUTH, verify=False)
    return response.json()

def dsystem_start_noaa(file_a0, region):
    headers = {"Content-Type": "application/json"}
    command = f'[ "start", "term.proj.irods", "{file_a0}", "{region}" ]'
    response = httpx.post(config.URL_DSYSTEM, headers=headers, content=command, auth=config.AUTH, verify=False)
    return response.json()

def get_a0_files(date):
    dt = datetime.date.fromisoformat(date)
    URL_NOAA_A0_FILES = f'{config.URL_NOAA_A0}/{dt.year}/{dt.month:02d}/{dt.day:02d}'
    response = httpx.get(URL_NOAA_A0_FILES, auth=config.AUTH)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [link["href"] for link in soup.select('.extension-a0 > td > a')]
    return links

def get_result_url_file(task_id):
    url, file = None, None
    response = httpx.get(f'{config.URL_NOAA_RESULT}/{task_id}', auth=config.AUTH)
    if response.is_success:
        soup = BeautifulSoup(response.text, 'html.parser')
        file = soup.select_one('.extension-zip > td > a')
        if not file:
            return url, file
        file = file["href"]
        url = f'{config.URL_NOAA_RESULT}/{task_id}/{file}'
    return url, file

def irods_download(url, path):
    with open(path, 'wb') as f:
        f.write(httpx.get(url, auth=config.AUTH).content)

def reproject_raster(in_path, out_path, crs="EPSG:4326"):
    with rasterio.open(in_path) as src:
        src_crs = src.crs
        transform, width, height = calculate_default_transform(src_crs, crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()

        kwargs.update({
            'crs': crs,
            'transform': transform,
            'width': width,
            'height': height})

        with rasterio.open(out_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=crs,
                    resampling=Resampling.nearest)

def make_geotiff(path, zfile):
    with zipfile.ZipFile(path / zfile) as zf:
        files = zf.namelist()
        file = files[0]
        with zf.open(file) as f:
            data = f.read()
            b0, data = readproj2(data)
            prjmap = get_projmapper(b0)
            lon = b0['b0_proj_common']['lon'][0]
            lat = b0['b0_proj_common']['lat'][0]
            latsize = b0['b0_proj_common']['latSize'][0]
            lonsize = b0['b0_proj_common']['lonSize'][0]
            latres = b0['b0_proj_common']['latRes'][0]
            lonres = b0['b0_proj_common']['lonRes'][0]
            rows = b0['b0_proj_common']['scanNum'][0]
            cols = b0['b0_proj_common']['pixNum'][0]
            pt = b0['b0_proj_common']['projType'][0] - 1
            # ESPG:3395 - наш
            # ESPG:3857 - Web Mercator
            # ESPG:4326 - градусы равнопромежуточная
            # data = data.astype(float)
            tf = Transformer.from_crs("EPSG:4326", "EPSG:3395", always_xy=True)
            
            top_left = tf.transform(lon, lat + latsize)
            bottom_right = tf.transform(lon + lonsize, lat) 
            latres = (top_left[1] - bottom_right[1]) / rows 
            lonres = (bottom_right[0] - top_left[0]) / cols
            lon = top_left[0]
            lat = top_left[1]

            transform = Affine.translation(lon - lonres / 2, lat + latsize - latres / 2) * Affine.scale(lonres, latres)
            transform = rasterio.transform.from_origin(lon, lat, lonres, latres)
            new_dataset = rasterio.open(
                                        path / 'new.tif', 
                                        'w', 
                                        driver='GTiff', 
                                        height=rows, 
                                        width=cols, 
                                        count=1, 
                                        dtype=data.dtype, 
                                        crs='EPSG:3395',
                                        transform=transform,
                                    )
            new_dataset.write(data, 1)
            new_dataset.close()
            reproject_raster(path / 'new.tif', path / f'{file}.tif')
            old = path / 'new.tif'
            old.unlink()
            return path / f'{file}.tif'

def run_noaa(params):
    # common
    results = []
    job_id = params['job_id']
    date = str(params['date'])
    region =  params['region'].value
    root = get_or_create_dir(config.DOWNLOAD_DIR, job_id)

    # validate params
    res = validate_noaa_params(params)
    if not res['success']:
        return res
    try:
        # specific
        files = get_a0_files(date)
        if not files:
            return error("На указанную дату нет снимков")
        dsystem_result = dsystem_start_noaa(random.choice(files), region)
        if dsystem_result['RC'] != 0:
            return error("Ошибка постановки задачи в dsystem")
        dsystem_task_id = dsystem_result['VALUE']
        with open('log.txt', 'a') as f:
            f.write(f'{dsystem_task_id}\n')
        # status = 'None'
        # count = 0
        # while status != 'FINISHED' and count < 60:
        #     sleep(5)
        #     try:
        #         status = dsystem_info(dsystem_task_id)['status']
        #     except Exception as e:
        #         pass
        #     count += 1
        # if count == 10:
        #     return error("Ошибка времени ожидания схемы - больше 60 попыток по 5 секунд")
        url, file = get_result_url_file(dsystem_task_id)
        count = 0
        while not url and count < 20:
            sleep(5)
            try:
                url, file = get_result_url_file(dsystem_task_id)
            except Exception as e:
                pass
            count += 1
        if count == 20:
            return error("Ошибка времени ожидания файла - больше 20 попыток по 5 секунд")
        
        irods_download(url, root / file)
        geotiff_file = make_geotiff(root, file)
        results.append(geotiff_file.as_posix())
    except Exception as e:
        return error(f"Неизвестная ошибка: {e}")
    return ready(results)
