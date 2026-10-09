# super dashboard

pip install -r requirements.txt
uvicorn app:app --port 8000
curl "localhost:8000/user?id=1"
curl "localhost:8000/user?id=%27%20OR%20%271%27=%271"
