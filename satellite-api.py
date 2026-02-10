from fastapi import FastAPI

app = FastAPI()

# to fetch a satellite's latest TLE
@app.get("/satellite_tle/{norad_id}")
def get_satellite_tle():
    return "Hello"

# to fetch all of a satellite's TLEs
# meaning that we have to store all the old TLEs
# per norad, maintain a dictionary of -> norad: [TLEs]
@app.get("/satellite_tle/{norad_id}")
def get_all_tles():
    return None

# to add a custom tle for a satellite
# since we cannot access the public tle data due to restrictions
# this custom tle will go in our local storage of all tles
@app.post("/satellite_tle/{norad_id}")
def add_custom_tle():
    return None