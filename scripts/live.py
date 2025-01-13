import re
import json
import requests


_reg_locations = re.compile(r"const locations = (.*);")
_reg_validations = re.compile(r"const live_validations = (.*);")
_url = "https://oma.enkora.fi/unisport/populartimes"

resp = requests.get(_url)
locations = json.loads(_reg_locations.search(resp.text).group(1))
validations = json.loads(_reg_validations.search(resp.text).group(1))
print(validations)
for loc_id in locations:
    print(locations[loc_id])
    print(validations.get(loc_id))
    print()
