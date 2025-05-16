# Import necessary modules
from flask import Flask, request, jsonify, render_template, Response
from io import StringIO
import sqlite3
import os
import re
import ipaddress
import csv
from functools import wraps
from dotenv import load_dotenv
from config.version import APP_VERSION, APP_MODE

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables (or use a default one)
API_KEY = os.environ.get('API_KEY', 'n4tX7f92Jw92kQeT!sEcReT_k3y')
if not API_KEY:
    raise RuntimeError("❌ API_KEY is not set. Define it in your .env file.")

# Initialize Flask app
app = Flask(__name__)
DB_NAME = 'equipements.db'

# Initialize the database and create table if it doesn't exist
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS equipements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                type TEXT NOT NULL,
                ip TEXT NOT NULL,
                mac TEXT,
                vlan TEXT,
                location TEXT,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

# Export equipment data in JSON or CSV format
@app.route('/export')
def export():
    fmt = request.args.get('format', 'json')
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute('SELECT * FROM equipements')
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

    if fmt == 'csv':
        si = StringIO()
        writer = csv.DictWriter(si, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
        return Response(
            si.getvalue(),
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=equipements.csv"}
        )
    return jsonify(data)

# Inject version and mode info into templates
@app.context_processor
def inject_version():
    return dict(app_version=APP_VERSION, app_mode=APP_MODE)

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for inventory page
@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

# Decorator to enforce API key authentication
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# Validate IP address format
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# Validate MAC address format (optional)
def is_valid_mac(mac):
    if not mac:
        return True
    return re.match(r'^([0-9A-Fa-f]{2}[:\-]){5}([0-9A-Fa-f]{2})$', mac)

# Validate incoming equipment data
def validate_equipement_data(data):
    for field in ['nom', 'type', 'ip']:
        if field not in data or not str(data[field]).strip():
            return f'Missing or empty required field: {field}'
    if not is_valid_ip(data['ip']):
        return 'Invalid IP format'
    if not is_valid_mac(data.get('mac')):
        return 'Invalid MAC format'
    return None

# Get all equipment records with optional filters
@app.route('/equipements', methods=['GET'])
def get_all():
    location = request.args.get('location')
    vlan = request.args.get('vlan')
    query = 'SELECT * FROM equipements WHERE 1=1'
    params = []

    if location:
        query += ' AND location = ?'
        params.append(location)
    if vlan:
        query += ' AND vlan = ?'
        params.append(vlan)

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(query, params)
        items = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    return jsonify(items)

# Get a single equipment record by ID
@app.route('/equipements/<int:id>', methods=['GET'])
def get_one(id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute('SELECT * FROM equipements WHERE id=?', (id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': f'Equipment with id {id} not found'}), 404
        return jsonify(dict(zip([col[0] for col in cursor.description], row)))

# Create a new equipment record
@app.route('/equipements', methods=['POST'])
@require_api_key
def create():
    data = request.get_json()
    error = validate_equipement_data(data)
    if error:
        return jsonify({'error': error}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            'INSERT INTO equipements (nom, type, ip, mac, vlan, location) VALUES (?, ?, ?, ?, ?, ?)',
            (data['nom'], data['type'], data['ip'], data.get('mac'), data.get('vlan'), data.get('location'))
        )
        return jsonify({'id': cursor.lastrowid}), 201

# Update an existing equipment record
@app.route('/equipements/<int:id>', methods=['PUT'])
@require_api_key
def update(id):
    data = request.get_json()
    error = validate_equipement_data(data)
    if error:
        return jsonify({'error': error}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            'UPDATE equipements SET nom=?, type=?, ip=?, mac=?, vlan=?, location=? WHERE id=?',
            (data['nom'], data['type'], data['ip'], data.get('mac'), data.get('vlan'), data.get('location'), id)
        )
        if cursor.rowcount == 0:
            return jsonify({'error': f'Equipment with id {id} not found'}), 404
    return jsonify({'message': 'Equipment updated successfully'})

# Delete an equipment record
@app.route('/equipements/<int:id>', methods=['DELETE'])
@require_api_key
def delete(id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('DELETE FROM equipements WHERE id=?', (id,))
    return jsonify({'message': 'Equipment deleted successfully'})

# Custom handler for 404 errors
@app.errorhandler(404)
def handle_404(e):
    return jsonify({'error': 'Route not found'}), 404

# Custom handler for 400 errors
@app.errorhandler(400)
def handle_400(e):
    return jsonify({'error': 'Invalid request'}), 400

# Start the Flask application
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
