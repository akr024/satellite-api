import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx, requests

app = FastAPI()

# ideally, in production, this would be redis cache
# but this dictionary cache in-memory is technically faster, hence used.
cache = {}

def epoch_parser(raw_response):
    year = int(raw_response["line1"][18:20])
    year = 2000 + year if year < 57 else 1900 + year
    day = float(raw_response["line1"][20:32])
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

# to fetch a satellite's latest TLE
@app.get("/satellite_tle/{norad_id}")
def get_satellite_tle():
    return "Hello"

# to fetch all of a satellite's TLEs
# meaning that we have to store all the old TLEs
# per norad, maintain a dictionary of -> norad: [TLEs]
@app.get("/satellite_tle/{norad_id}/history")
def get_all_tles():
    return None

# to add a custom tle for a satellite
# since we cannot access the public tle data due to restrictions
# this custom tle will go in our local storage of all tles
@app.post("/satellite_tle/{norad_id}")
def add_custom_tle():
    return None