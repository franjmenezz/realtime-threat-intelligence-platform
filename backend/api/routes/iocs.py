"""IoCs Route."""
import random, time, uuid
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

class IoC(BaseModel):
    event_id: str; ioc_type: str; ioc_value: str; source: str
    confidence: float; tags: list[str]; country_code: Optional[str]
    country_name: Optional[str]; asn: Optional[str]; isp: Optional[str]
    abuse_score: Optional[int]; risk_score: float; risk_level: str
    ingested_at: int; enriched_at: Optional[int]

class PaginatedIoCs(BaseModel):
    items: list[IoC]; total: int; page: int; size: int; pages: int

_TYPES = ["ip","domain","hash","url"]
_SOURCES = ["abuseipdb","virustotal","alienvault_otx","feodo_tracker","mock"]
_TAGS = ["malware","ransomware","c2","phishing","botnet","tor-exit-node","scanner","brute-force"]
_COUNTRIES = [("RU","Russia"),("CN","China"),("US","United States"),("DE","Germany"),("NL","Netherlands")]
_VALUES = {"ip":["185.220.101.47","45.142.212.100","91.108.4.1"],"domain":["update-service-cdn.com","secure-login-portal.net"],"hash":["e3b0c44298fc1c14","a87ff679a2f3e71d"],"url":["http://185.220.101.47/payload.exe"]}

def _mock(seed=None):
    random.seed(seed)
    t = random.choice(_TYPES)
    s = round(random.uniform(0,100),2)
    l = next(lv for lv,th in [("CRITICAL",80),("HIGH",60),("MEDIUM",40),("LOW",20),("INFO",0)] if s>=th)
    cc,cn = random.choice(_COUNTRIES)
    now = int(time.time()*1000)
    r = {"event_id":str(uuid.uuid4()),"ioc_type":t,"ioc_value":random.choice(_VALUES[t]),"source":random.choice(_SOURCES),"confidence":round(random.uniform(0.4,1.0),2),"tags":random.sample(_TAGS,k=random.randint(1,3)),"country_code":cc,"country_name":cn,"asn":f"AS{random.randint(1000,60000)}","isp":random.choice(["LeaseWeb","Hetzner","OVH"]),"abuse_score":random.randint(0,100),"risk_score":s,"risk_level":l,"ingested_at":now-random.randint(0,3600000),"enriched_at":now-random.randint(0,1800000)}
    random.seed(None)
    return r

@router.get("", response_model=PaginatedIoCs)
async def list_iocs(page:int=Query(1,ge=1), size:int=Query(20,ge=1,le=100), ioc_type:Optional[str]=None, risk_level:Optional[str]=None):
    items = [_mock(i+page*size) for i in range(size)]
    if risk_level: items = [i for i in items if i["risk_level"]==risk_level]
    if ioc_type: items = [i for i in items if i["ioc_type"]==ioc_type]
    return PaginatedIoCs(items=[IoC(**i) for i in items],total=248,page=page,size=size,pages=(248+size-1)//size)

@router.get("/{event_id}", response_model=IoC)
async def get_ioc(event_id:str): return IoC(**_mock(42))

@router.post("/search", response_model=PaginatedIoCs)
async def search_iocs(body:dict):
    items=[_mock(i) for i in range(body.get("limit",20))]
    return PaginatedIoCs(items=[IoC(**i) for i in items],total=len(items),page=1,size=len(items),pages=1)
