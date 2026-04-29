"""Stats Route."""
import random, time
from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
async def get_summary():
    return {"total_iocs":10284,"iocs_last_24h":432,"critical_alerts":18,"high_alerts":76,"sources_active":4,"avg_risk_score":52.4,"top_ioc_type":"ip","top_country":"RU","processing_lag_ms":312}

@router.get("/by-type")
async def get_by_type():
    return [{"type":"ip","count":4923,"pct":48},{"type":"domain","count":2671,"pct":26},{"type":"hash","count":1641,"pct":16},{"type":"url","count":1049,"pct":10}]

@router.get("/by-country")
async def get_by_country():
    return [{"country_code":"RU","country_name":"Russia","count":2847},{"country_code":"CN","country_name":"China","count":2103},{"country_code":"US","country_name":"United States","count":1029},{"country_code":"DE","country_name":"Germany","count":621},{"country_code":"NL","country_name":"Netherlands","count":498}]

@router.get("/timeline")
async def get_timeline():
    now = int(time.time())
    return [{"hour":now-(23-i)*3600,"count":random.randint(10,120),"critical":random.randint(0,10)} for i in range(24)]
