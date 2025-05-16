
# 🛠 Full Version – Network Inventory API

This folder contains the **complete version** of the Flask-based Network Inventory API.

It supports full **CRUD** operations (Create, Read, Update, Delete) and uses a simple API key protection.

---

## 🔧 How to Run Locally

1. Create a `.env` file at the root of the project and add your API key:
   
   API_KEY=n4tX7f92Jw92kQeT!sEcReT_k3y

2. Install dependencies:

   pip install -r requirements.txt

3. Start the server:

   python app.py

The app will run at http://localhost:5000

---

## 🔐 API Key Header

For write operations (POST, PUT, DELETE), you must include this HTTP header:

    x-api-key: n4tX7f92Jw92kQeT!sEcReT_k3y

---

## 📡 Endpoints

- GET /equipements — List all equipment
- GET /equipements/<id> — Retrieve specific equipment
- POST /equipements — Add new equipment (requires API key)
- PUT /equipements/<id> — Update existing equipment (requires API key)
- DELETE /equipements/<id> — Delete equipment (requires API key)
- GET /export?format=csv — Export equipment data to CSV

---

## 🖥 Frontend

You can also use the `/inventory` route to access a basic frontend that interacts with the API.

---

## 📄 License

MIT License
