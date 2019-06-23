import requests
from requests import *
payload = {'page': 2}
users = requests.get('http://localhost:5000/api/users')
print(users.text)
