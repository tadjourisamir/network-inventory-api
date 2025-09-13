![new](https://github.com/user-attachments/assets/8163f838-3ff6-48fd-b346-71bc950692b1)

# 🌐 Network Inventory API – Lightweight RESTful API

**A simple and lightweight RESTful API built with Flask and SQLite to manage a small inventory of network devices (switches, routers, access points...).**

This project includes two versions:
- 🧪 A **demo version** (read-only) for public viewing
-⚙️ A **full version** (CRUD enabled) for local or containerized deployment

Ideal for learning, testing, and demonstration purposes.

------------------------------------------------------------

🚀 Live Demo
------------

A public, read-only demo is available at:

🔗 https://network-inventory-api-demo.onrender.com/

> Demo mode allows only `GET` requests.
> For full functionality (POST / PUT / DELETE), use the local full version.

------------------------------------------------------------

💻 Full Version - Local Usage
-----------------------------

To run the full version locally:

1. Clone the repository
2. Navigate to the `full-version/` folder
3. Install dependencies:
   pip install -r requirements.txt
4. Start the app:
   python app.py

Then open: http://localhost:5000

------------------------------------------------------------

🐳 Docker Usage
---------------

The full version is Docker-ready. To run it with Docker:

1. Build the Docker image:
   docker build -t network-inventory .

2. Run the container:
   docker run -p 5000:5000 network-inventory

App will be available at: http://localhost:5000

------------------------------------------------------------

📁 Project Structure
--------------------

```txt
network-inventory-api/
├── demo/              → Read-only version (GET only)
├── full-version/      → Full version with Docker support
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config/
│   ├── templates/
│   └── static/
├── README.txt
├── .gitignore
```

------------------------------------------------------------

🛠️ Technologies Used
---------------------

- 🐍 Python 3.12.3  
- 🫙 Flask 3.1.0  
- 🛢 SQLite 3.45.3  
- 🌐 HTML & CSS  
- ⚙️ JavaScript  
- 🐳 Docker 28.0.4

------------------------------------------------------------

📄 License
----------

This project is released under the MIT License.
