from flask import Flask, jsonify, request, url_for
import mysql.connector
from mysql.connector import Error, cursor
from flask_cors import CORS
from flask import Flask, render_template, request, redirect


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Konfigurimi i lidhjes me databazën MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'paketadb'
}

# Funksion për krijimin e lidhjes me databazën
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

# funksion per databazen per te krijuar tabelat nqs nuk ekzistone
def init_db():
    conn = get_db_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        # Krijo tabelen 'paketat'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paketat (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numriPaketes VARCHAR(50),
                emriDerguesit VARCHAR(100),
                kohaArdhjes DATE,
                vendodhjaPakos VARCHAR(100),
                email VARCHAR(100),
                adresa TEXT,
                emriMarresit VARCHAR(100),
                eshteDorezuar BOOLEAN DEFAULT FALSE,
                status VARCHAR(20) DEFAULT 'Pending'
            )
        ''')
        # Krijon tabelën 'users' për autentifikim
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                password VARCHAR(50),
                role VARCHAR(20)
            )
        ''')
        conn.commit()
        print("Tables 'paketat' and 'users' created or already exist.")
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Endpoint për të marrë një pako në bazë të numrit të saj
@app.route('/paketat/<string:numri_paketes>', methods=['GET'])
def get_package(numri_paketes):
    numri_paketes = numri_paketes.strip()
    print(f"Input i marrë: '{numri_paketes}'")  # Debug
    if not numri_paketes:
        print("Kërkesë me numër pakete bosh")
        return jsonify({"message": "Numri i paketës është i pavlefshëm"}), 400
    conn = get_db_connection()
    if conn is None:
        print("Dështoi lidhja me databazën")
        return jsonify({"message": "Gabim gjatë lidhjes me databazën"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM paketat WHERE numriPaketes = %s"
        cursor.execute(query, (numri_paketes,))
        result = cursor.fetchone()
        print(f"Kërkesa për numriPaketes='{numri_paketes}', rezultati: {result}")
        if result:
            print(f"Pakoja u gjet: {result}")
            return jsonify(result), 200
        else:
            print(f"Nuk u gjet asnjë pako për numriPaketes='{numri_paketes}'")
            return jsonify({"message": "Pakoja nuk u gjet"}), 404
    except Error as e:
        print(f"Gabim në databazë për numriPaketes='{numri_paketes}': {e}")
        return jsonify({"message": "Gabim gjatë lidhjes me databazën", "error": str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# # Endpoint për login të përdoruesve në bazë të username, password dhe role
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username, password, role = data.get('username'), data.get('password'), data.get('role')
    print(f"Kërkesa për login: {data}")
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Gabim gjatë lidhjes me databazën"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = %s"
        cursor.execute(query, (username, password, role))
        user = cursor.fetchone()
        print(f"Rezultati i query-it: {user}")
        if user:
            if role == "admin":
                return jsonify({"redirect": "Administrator.html"})
            elif role == "courier":
                return jsonify({"redirect": "Courier.html"})
            return jsonify({"message": "Role i panjohur"}), 400
        return jsonify({"message": "Invalid credentials", "status": 401}), 401
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Database connection error", "error": str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Endpoint për të marrë pakot me kërkim opsional dhe limitim në 5
@app.route('/api/paketat', methods=['GET'])
def get_packages():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Gabim gjatë lidhjes me databazën"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        if search_query:
            query = "SELECT * FROM paketat WHERE numriPaketes LIKE %s LIMIT 5"
            cursor.execute(query, (f'%{search_query}%',))
        else:
            query = "SELECT * FROM paketat LIMIT 5"
            cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"message": "Gabim me API", "error": str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Endpoint për të shtuar një pako të re në databazë
@app.route('/api/paketat', methods=['POST'])
def add_package():
    data = request.get_json()
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Gabim gjatë lidhjes me databazën"}), 500
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO paketat (numriPaketes, emriDerguesit, kohaArdhjes, vendodhjaPakos, 
                                emriMarresit, email, adresa, eshteDorezuar)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['numriPaketes'], data['emriDerguesit'], data['kohaArdhjes'], data['vendodhjaPakos'],
            data.get('emriMarresit', ''), data['email'], data['adresa'], data['eshteDorezuar']
        )
        cursor.execute(query, values)
        conn.commit()
        return jsonify({'message': 'Paketa u shtua me sukses'}), 201
    except Error as e:
        print(f"Error adding package: {e}")
        return jsonify({'message': 'Gabim gjatë shtimit të pakos', 'error': str(e)}), 400
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Endpoint për të rivendosur statusin e dorëzimit të një pakoje
@app.route('/api/paketat/deliver/<numriPaketes>', methods=['PUT'])
def mark_as_delivered(numriPaketes):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Gabim gjatë lidhjes me databazën"}), 500
    try:
        cursor = conn.cursor()
        query = "UPDATE paketat SET eshteDorezuar = TRUE WHERE numriPaketes = %s"
        cursor.execute(query, (numriPaketes,))
        conn.commit()
        return jsonify({'message': 'Paketa u shënua si e dorëzuar'}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Gabim me API', 'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Reset delivery status
@app.route('/api/paketat/reset/<numriPaketes>', methods=['PUT'])
def reset_delivery(numriPaketes):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Gabim gjatë lidhjes me databazën"}), 500
    try:
        cursor = conn.cursor()
        query = "UPDATE paketat SET eshteDorezuar = FALSE WHERE numriPaketes = %s"
        cursor.execute(query, (numriPaketes,))
        conn.commit()
        return jsonify({'message': 'Statusi i pakos u rivendos'}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Gabim me API', 'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Delete package
@app.route('/api/paketat/<numriPaketes>', methods=['DELETE'])
def delete_package(numriPaketes):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Gabim gjatë lidhjes me databazën"}), 500
    try:
        cursor = conn.cursor()
        query = "DELETE FROM paketat WHERE numriPaketes = %s"
        cursor.execute(query, (numriPaketes,))
        conn.commit()
        return jsonify({'message': 'Paketa u fshi me sukses'}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Gabim me API', 'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------- Courier Page -----------------------------------------------

# Serve Courier.htm

@app.route('/')
def home():
    return app.send_static_file('/html/Courier.html')

# Search endpoint (exact match)
@app.route('/search', methods=['GET'])
def search_packages():
    search = request.args.get('search', '')
    print(f"Search query: {search}")
    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM paketat WHERE numriPaketes = %s"
        cursor.execute(query, (search,))
        package = cursor.fetchone()
        print(f"Found package: {package}")
        if package:
            print(f"Returning JSON: {package}")
            return jsonify(package)
        else:
            print("No package found")
            return jsonify({})
    except Error as e:
        print(f"Query error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Update location endpoint
@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.form
    package_id = data.get('numriPaketes')
    new_location = data.get('location')
    print(f"Updating package {package_id} to {new_location}")

    if not package_id or not new_location:
        print("Missing numriPaketes or location")
        return jsonify({'success': False, 'error': 'Missing numriPaketes or location'}), 400

    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        query = "UPDATE paketat SET vendodhjaPakos = %s WHERE numriPaketes = %s"
        cursor.execute(query, (new_location, package_id))
        conn.commit()
        print("Update successful")
        return jsonify({'success': True})
    except Error as e:
        print(f"Update error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ------------------------------------- Submit Data from Admin Panel-------------------------------------

@app.route('/submit-package', methods=['POST'])
def submit_package():
    try:
        numri_paketes = request.form['numriPaketes']
        emri_derguesit = request.form['emriDerguesit']
        koha_ardhjes = request.form['kohaArdhjes']
        vendodhja_pakos = request.form['vendodhjaPakos']
        emri_marresit = request.form['emriMarresit']
        email = request.form['email']
        adresa = request.form['adresa']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO paketat (numriPaketes, emriDerguesit, kohaArdhjes,  vendodhjaPakos, emriMarresit, email, adresa)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (numri_paketes, emri_derguesit, koha_ardhjes, vendodhja_pakos, emri_marresit, email, adresa)

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('success'))  # Ridrejto në faqen e suksesit

    except mysql.connector.Error as err:
        return f"Gabim gjatë shtimit në databazë: {err}", 500

@app.route('/success')
def success():
    return "✅ Të dhënat u shtuan me sukses në databazë!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


