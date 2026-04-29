"""Alerts Route."""
import random, time, uuid
from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def list_alerts(limit:int=20):
    alerts=[]
    for i in range(limit):
        random.seed(i)
        alerts.append({"alert_id":str(uuid.uuid4()),"event_id":str(uuid.uuid4()),"ioc_value":random.choice(["185.220.101.47","update-service-cdn.com","e3b0c44298fc1c14"]),"ioc_type":random.choice(["ip","domain","hash"]),"risk_level":random.choice(["CRITICAL","HIGH"]),"risk_score":round(random.uniform(60,100),2),"rule_name":random.choice(["TOR_EXIT_NODE","HIGH_VT_SCORE","ABUSE_THRESHOLD","KNOWN_C2"]),"description":"IoC exceeded risk threshold.","country_code":random.choice(["RU","CN","US","UA"]),"created_at":int(time.time()*1000)-random.randint(0,86400000)})
    random.seed(None)
    return {"items":alerts,"total":limit}
