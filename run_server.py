import os
import requests
import sys

#external_ip = requests.get('https://api.ipify.org').text
#print("External IP: " + external_ip)

os.system("python -m flask --app main.py run --host=0.0.0.0 --port=80 --with-threads")