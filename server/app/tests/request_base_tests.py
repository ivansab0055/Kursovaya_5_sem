"""
Тест запроса через `requests`
"""

import json

import requests

user = json.dumps(
    {
        "email": "test@test.com",
        "company": "Test corp",
        "password": "mycoolpassword"
    }
)

res = requests.post('http://localhost:8000/api/auth/signup', headers={"Content-Type": "application/json"}, data=user)
print('response from server:', res.status_code)

data = res.json()
print(data)
