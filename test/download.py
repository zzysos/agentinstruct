import json
import os
from typing import List, Dict

from helm.common.hierarchical_logger import hlog

import requests

def download_file(url, target_path):
    response = requests.get(url)
    with open(target_path, 'wb') as file:
        file.write(response.content)

# 示例用法
url = "https://raw.githubusercontent.com/chuanyang-Zheng/Progressive-Hint/main/dataset/AddSub/AddSub.json"
target_path = "../mydataset/addsub.json"

# download_file(url, target_path)

with open(target_path, 'r') as file:
    json_data = json.load(file)
print(json_data)

print(len(json_data))