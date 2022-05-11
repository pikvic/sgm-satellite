from datetime import date
from enum import Enum
from pydantic import BaseModel

class NoaaRegionEnum(str, Enum):
    japsea = 'JapSea.cfg', 
    kuril = 'Kuril.cfg', 
    nwpac = 'NWPac.cfg', 
    okhnwpo = 'OkhNWPO.cfg', 
    okhsea = 'OkhSea.cfg'

class TaskResult(BaseModel):
    ready: bool = False
    results: list[str] = None
    
class TaskPostResult(BaseModel):
    job_id: str
    url: str
    
class NoaaTaskParams(BaseModel):
    date: date
    region: NoaaRegionEnum
    