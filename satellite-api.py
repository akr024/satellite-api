import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx, requests

app = FastAPI()

# ideally, in production, this would be redis cache
# but this dictionary cache in-memory is technically faster, hence used.
cache = {}

def epoch_parser(line1):
    year = int(line1[18:20])
    year = 2000 + year if year < 57 else 1900 + year
    day = float(line1[20:32])
    epoch = datetime(year, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(days=day - 1)
    return str(epoch)

# function to fetch the latest data of a satellite
async def fetch_from_celestrak(norad_id):
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=2LE"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Satellite data not found!")
        lines = response.text.strip().split('\n')
        return lines[0], lines[1]

# to fetch a satellite's latest TLE, as stored in the cache
@app.get("/satellite_tle/{norad_id}")
async def get_satellite_tle(norad_id):
    fetch_from_cache = False

    if norad_id not in cache: #meaning that the norad id is not present in the cache as a key
        fetch_from_cache = True
        cache[norad_id] = []
    else:
        latest_tle = cache[norad_id][0] #the first index stores the latest epoch TLE
        if (datetime.now(datetime.timezone.utc) - latest_tle['fetch_time']) > datetime.timedelta(hours=1):
            fetch_from_cache = True
    
    if fetch_from_cache:
        line1, line2 = await fetch_from_celestrak(norad_id)
        epoch = epoch_parser(line1)
        cache[norad_id].insert(0, {
            "line1": line1,
            "line2": line2,
            "epoch": epoch,
            "fetch_time": datetime.now(datetime.timezone.utc),
            "source": "celestrak"
        })

    latest = cache[norad_id][0]
    return {
        'line1': latest["line1"],
        'line2': latest["line2"],
        'epoch': latest["epoch"],
        'fetch_time': latest["fetch_time"].isoformat(),
        'source': latest['source']
    }

# to fetch all of a satellite's TLEs
# meaning that we have to store all the old TLEs
# per norad, maintain a dictionary of -> norad: [TLEs]
@app.get("/satellite_tle/{norad_id}/history")
def get_all_tles(norad_id):
    if norad_id not in cache:
        raise HTTPException(status_code=404, detail="No data found")

    tleHistory = []

    for tle in cache[norad_id]:
        tleHistory.append(tle)

    return tleHistory

# to add a custom tle for a satellite
# since we cannot access the public tle data due to restrictions
# this custom tle will go in our local storage of all tles
@app.post("/satellite_tle/{norad_id}")
def add_custom_tle(norad_id, new_tle):
    epoch = epoch_parser(new_tle.line1) #since new_tle is just an object with line1
    # alternatively, if it's a dictionary of string: string mapping
    # I could use epoch_parser(new_tle["line1"])
    if norad_id not in cache:
        cache[norad_id] = []
    
    cache[norad_id].insert(0, {
        'line1': new_tle.line1,
        'line2': new_tle.line2,
        'epoch': epoch,
        'fetch_time': datetime.now(datetime.timezone.utc),
        'source': 'client'
    })

    cache.sort(key=lambda x: x["epoch"], reverse=True) # because this new insertion/update might be of an old TLE
    
    return {
        "status": "success"
    }