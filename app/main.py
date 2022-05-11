from fastapi import FastAPI, HTTPException, status, Request, APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from rq.job import Job

import app.config as config
from app.schema import TaskResult, TaskPostResult, NoaaTaskParams
from app.queue import get_queue, get_redis, get_jobs_in_registries, create_task
from app.tasks import run_noaa



app = FastAPI(
    title='Вычислительный узел "Обработка спутниковых данных"',
    description="Данный вычислительный узел содержит API для различных процедур обработки спутниковых данных",
    version="0.1"
)

if not config.DOWNLOAD_DIR.exists():
    config.DOWNLOAD_DIR.mkdir()

app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.get("/noaa")
# def get_noaa(date: str, region: int):
#     auth = requests.auth.HTTPBasicAuth(config.USER, config.PASSWORD)
#     configs = ['JapSea.cfg', 'Kuril.cfg', 'NWPac.cfg', 'OkhNWPO.cfg', 'OkhSea.cfg']
#     url = 'https://dsystem.satellite.dvo.ru:4004/dsystem'
#     url_a0 = 'https://davrods.satellite.dvo.ru/data/NOAA'
#     url_result = 'https://davrods.satellite.dvo.ru/process/result/term.proj.irods'
#     dt = datetime.date.fromisoformat(date)
#     url_a0_files = f'{url_a0}/{dt.year}/{dt.month:02d}/{dt.day:02d}'
#     res = requests.get(url_a0_files, auth=auth)
#     soup = BeautifulSoup(res.text, 'html.parser')
#     links = [link["href"] for link in soup.select('.extension-a0 > td > a')]
#     command = f'[ "start", "term.proj.irods", "{links[0]}", "{configs[region]}" ]'
#     headers = {"Content-Type": "application/json"}
#     res = requests.post(url, headers=headers, data=command, auth=auth, verify=False)
#     task_id = res.json()["VALUE"]
#     sleep(10)
#     res = requests.get(f'{url_result}/{task_id}', auth=auth)
#     print(f'{url_result}/{task_id}')
#     while not res.ok:
#         res = requests.get(f'{url_result}/{task_id}', auth=auth)
#         sleep(10)
#     if res.ok:
#         soup = BeautifulSoup(res.text, 'html.parser')
#         file = soup.select_one('.extension-zip > td > a')["href"]
#         url = f'{url_result}/{task_id}/{file}'
#         with open(config.DOWNLOAD_DIR / file, 'wb') as f:
#             f.write(requests.get(url, auth=auth).content)
#     host = "http://127.0.0.1:8000"
#     return {"status": "ok", "url": f"{host}/{(config.DOWNLOAD_DIR / file).as_posix()}"}

@app.get(
    "/",
    summary="Проверка работы узла",
    description="Возвращает Hello, World!, если работает."
)
def root():
    return {"message": "Hello World!"}

@app.get(
    "/jobs",
    summary="Получение списка всех задач",
    description="Возвращает список всех задач."
)
def jobs_list():
    return get_jobs_in_registries()

@app.get(
    "/results/{job_id}",
    name='get_result',
    response_model=TaskResult,
    summary="Получение результата по задаче",
    description="Возвращает состояние задачи и результат, если есть."
)
def get_result(job_id):
    try:
        job = Job.fetch(job_id, connection=get_redis())
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found!')
    if job.is_finished:
        res = job.result
        if 'error' in res:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=res['error'])
        return TaskResult(**res)
    else:
        return TaskResult(ready=False)

@app.post(
    "/noaa",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskPostResult
)
def noaa_post(params: NoaaTaskParams, request: Request):
    print(params.dict()['region'].value)
    res = create_task(run_noaa, params.dict())
    res['url'] = request.url_for('get_result', job_id=res['job_id'])
    return TaskPostResult(**res)


# @app.get(
#     "/download/{job_id}/{filename}",
#     summary="Скачивание файла с результатом по задаче",
#     description="Возвращает конкретный файл с результатом."
# )
# def get_file(job_id, filename):
#     path = config.DOWNLOAD_DIR / job_id / filename
#     if path.exists():
#         return FileResponse(str(path))
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found!')

