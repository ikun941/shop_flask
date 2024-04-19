import requests
import json
import time

start = time.time()
response = requests.post("http://47.115.210.52:5000/select_shop", json={"shop_name": "火锅",
                                                                     "start": 70,
                                                                     "end": 100})
data = response.text
end = time.time()

json_data = json.loads(data)
print("响应时间:", end-start)
print(json_data)




