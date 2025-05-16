from flask import Flask, request, jsonify, render_template, Response
from io import StringIO
import sqlite3
import os
import re
import ipaddress
import csv
from functools import wraps
from config.version import APP_VERSION, APP_MODE



# Simple API key
API_KEY = os.environ.get('API_KEY', 'mysecretapikey')


app = Flask(__name__)
DB_NAME = 'equipements.db'

# Creating the database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            '''
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
            '''
        )

@app.context_processor
def inject_version():
    return dict(app_version=APP_VERSION, app_mode=APP_MODE)

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
        output = si.getvalue()
        return Response(
            output,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=equipements.csv"}
        )
    else:
        return jsonify(data)
    

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

# Decorator to protect routes with the API key
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# Strict IP address validation
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# MAC address validation 
def is_valid_mac(mac):
    if not mac:
        return True
    pattern = r'^([0-9A-Fa-f]{2}[:\-]){5}([0-9A-Fa-f]{2})$'
    return re.match(pattern, mac)

# Centralized data validation
def validate_equipement_data(data):
    required_fields = ['nom', 'type', 'ip']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return f'Missing or empty required field: {field}'
    if not is_valid_ip(data['ip']):
        return 'Invalid IP format'
    if not is_valid_mac(data.get('mac')):
        return 'Invalid MAC format'
    return None

@app.route('/')
def index():
    return render_template('index.html')

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

def seed_data():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute('SELECT COUNT(*) FROM equipements')
        if cur.fetchone()[0] == 0:
            equipements = [
                ("Switch A", "Switch", "192.168.1.1", "AA:BB:CC:DD:EE:01", "10", "Salle 1"),
                ("Routeur B", "Routeur", "192.168.1.254", "AA:BB:CC:DD:EE:02", "20", "Salle 2"),
                ("AP Wifi C", "Point d'accès", "192.168.2.1", "AA:BB:CC:DD:EE:03", "30", "Hall"),
                ("Switch D", "Switch", "192.168.3.1", "AA:BB:CC:DD:EE:04", "40", "Salle Serveurs"),
                ("Routeur E", "Routeur", "10.0.0.1", "AA:BB:CC:DD:EE:05", "50", "Bureau Réseau"),
                ("Firewall F", "Pare-feu", "10.0.0.254", "AA:BB:CC:DD:EE:06", "60", "Datacenter"),
                ("Switch G", "Switch", "172.16.0.1", "AA:BB:CC:DD:EE:07", "70", "RDC"),
                ("AP Wifi H", "Point d'accès", "172.16.0.10", "AA:BB:CC:DD:EE:08", "80", "Etage 1"),
                ("Modem I", "Modem", "192.0.2.1", "AA:BB:CC:DD:EE:09", "90", "Local Technique"),
                ("Bridge J", "Bridge", "198.51.100.1", "AA:BB:CC:DD:EE:10", "100", "Toit")
            ]

            conn.executemany(
                "INSERT INTO equipements (nom, type, ip, mac, vlan, location) VALUES (?, ?, ?, ?, ?, ?)",
                equipements
            )


@app.route('/equipements/<int:id>', methods=['GET'])
def get_one(id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute('SELECT * FROM equipements WHERE id=?', (id,))
        row = cursor.fetchone()
    if not row:
        return jsonify({'error': f'Equipment with id {id} not found'}), 404
    return jsonify(dict(zip([col[0] for col in cursor.description], row)))

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
        new_id = cursor.lastrowid
    return jsonify({'id': new_id}), 201

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

@app.route('/equipements/<int:id>', methods=['DELETE'])
@require_api_key
def delete(id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('DELETE FROM equipements WHERE id=?', (id,))
    return jsonify({'message': 'Equipment deleted successfully'})

# Handling 404 errors
@app.errorhandler(404)
def handle_404(e):
    return jsonify({'error': 'Route not found'}), 404

# Handling 400 errors
@app.errorhandler(400)
def handle_400(e):
    return jsonify({'error': 'Invalid request'}), 400

# Starting the app
if __name__ == '__main__':
    init_db()
    seed_data()
    app.run(host="0.0.0.0", port=5000)