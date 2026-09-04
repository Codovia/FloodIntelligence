import urllib.request
import json

url = "https://nwdp.nwic.gov.in/api/v1/datasets/search?q=Rainfall+Karnataka"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print("Found datasets:", len(data.get("results", [])))
        for d in data.get("results", [])[:3]:
            print(d.get("title"))
except Exception as e:
    print("Error accessing NWDP:", e)
