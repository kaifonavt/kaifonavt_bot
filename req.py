import requests

OLLAMA_API = "http://localhost:11434/api"
response = requests.get(f"{OLLAMA_API}/status")
print(response.status_code)
print(response.text)
