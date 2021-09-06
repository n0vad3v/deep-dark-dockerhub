import requests
from influxdb import InfluxDBClient
import datetime

# CONFIG HERE
INFLUXDB_HOST = "127.0.0.1"
INFLUXDB_PORT = 8086
INFLUXDB_DB = "dockerhub"

INFLUXDB_TAG = "main-account"
# DON'T EDIT BELOW

def get_token():
    url = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull"
    r = requests.get(url)
    return r.json()['token']

def get_remain(token):
    url = "https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest"
    header_token = "Bearer " + token
    r = requests.head(url,headers={"Authorization":header_token})
    return r.headers['RateLimit-Remaining'].split(';')[0]

if __name__ == '__main__':
    remain = get_remain(get_token())
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT,database=INFLUXDB_DB)
    json_body = [
        {
            "measurement": "dockerhub-ratelimit",
            "tags": {
                "host": INFLUXDB_TAG,
            },
            "time": str(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")),
            "fields": {
                "remain": remain,
            }
        }
    ]
    client.write_points(json_body)
