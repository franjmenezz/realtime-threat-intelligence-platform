"""Stream Route — SSE."""
import asyncio, json, random, time, uuid
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

async def _generator():
    while True:
        event = {"event_id":str(uuid.uuid4()),"ioc_type":random.choice(["ip","domain","hash","url"]),"ioc_value":random.choice(["185.220.101.47","update-service-cdn.com","e3b0c44298fc"]),"source":random.choice(["abuseipdb","virustotal","mock"]),"risk_level":random.choice(["CRITICAL","HIGH","MEDIUM","LOW"]),"risk_score":round(random.uniform(0,100),2),"country_code":random.choice(["RU","CN","US","DE"]),"ingested_at":int(time.time()*1000)}
        yield f"data: {json.dumps(event)}\n\n"
        await asyncio.sleep(3)

@router.get("/iocs")
async def stream_iocs():
    return StreamingResponse(_generator(), media_type="text/event-stream", headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no","Access-Control-Allow-Origin":"*"})
