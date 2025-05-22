from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Konfigurimi i databazës MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'paketadb'
}

# Funksion për të krijuar lidhjen me databazën
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Gabim gjatë lidhjes me databazën: {e}")
        return None

# Krijimi i tabelave nëse nuk ekzistojnë
def init_db():
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numriPaketes VARCHAR(50),
                emriDerguesit VARCHAR(100),
                kohaArdhjes DATE,
                vendodhjaPakos VARCHAR(100),
                numriTelefonit VARCHAR(20),
                adresa TEXT,
                status VARCHAR(20) DEFAULT 'Pending'
            )
        ''')
        conn.commit()
        print("Tabela 'packages' u krijua ose ekziston tashmë.")
    except Error as e:
        print(f"Gabim gjatë inicializimit të databazës: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/paketat/<string:numri_paketes>', methods=['GET'])
def merr_paketen(numri_paketes):
    if not numri_paketes.strip():
        return jsonify({"message": "Numri i paketës është i pavlefshëm"}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Gabim gjatë lidhjes me databazën"}), 500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM packages WHERE numriPaketes = %s"
        cursor.execute(query, (numri_paketes,))
        result = cursor.fetchone()

        if result:
            return jsonify(result)
        else:
            return jsonify({"message": "Pakoja nuk u gjet"}), 404
    except Error as e:
        print(f"Gabim gjatë lidhjes me databazën: {e}")
        return jsonify({"message": "Gabim gjatë lidhjes me bazën e të dhënave", "error": str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Merr 5 paketa nga databaza
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    print(f"Kërkesa për login: {data}")
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Gabim gjatë lidhjes me databazën"}), 500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = %s"
        cursor.execute(query, (username, password, role))
        user = cursor.fetchone()

        print(f"Rezultati i query-it: {user}")

        if user:
            if role == "admin":
                return jsonify({"redirect": "Administrator.html"})
            elif role == "courier":
                return jsonify({"redirect": "Postier.html"})
            return jsonify({"message": "Role i panjohur"}), 400
        else:
            return jsonify({"message": "Invalid credentials", "status": 401}), 401
    except Error as e:
        print(f"Gabim nga databaza: {e}")
        return jsonify({"message": "Database connection error", "error": str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Merr 5 paketa nga databaza
@app.route('/api/packages', methods=['GET'])
def get_packages():
    try:
        # Merr parametrin e kërkimit nga query string (nëse ekziston)
        search_query = request.args.get('search', '')

        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Query për të marrë deri në 5 rreshta bazuar në kërkim
                query = """
                    SELECT * FROM paketat 
                    WHERE numriPaketes LIKE %s 
                    LIMIT 5
                """
                search_term = f"%{search_query}%"
                cursor.execute(query, (search_term,))
                results = cursor.fetchall()
                return jsonify(results), 200
    except Error as e:
        print(f"Gabim: {e}")
        return jsonify({"message": "Gabim me API", "error": str(e)}), 500




# ------------------ Ruajtja e Te dhenave Ne DataBase nga Faqja e Adminit ----------------------

@app.route('/submit-package', methods=['POST'])
def submit_package():
    # Merr të dhënat nga formulari dhe i cakton në variablin `data`
    data = request.form
    print(data)  # Debug: Shfaq të dhënat e formularit për t'u siguruar që janë marrë saktë

    try:
        # Krijo lidhjen me databazën
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO paketat (numriPaketes, emriDerguesit, kohaArdhjes, vendodhjaPakos, numriTelefonit, adresa)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (
                    data['numriPaketes'],  # Merr vlerat nga `data`
                    data['emriDerguesit'],
                    data['kohaArdhjes'],
                    data['vendodhjaPakos'],
                    data['numriTelefonit'],
                    data['adresa']
                )

                # Ekzekuto query
                cursor.execute(query, values)
                conn.commit()

        return jsonify({"message": "Data saved successfully!"}), 200

    except Error as e:
        print(f"Gabim gjatë ekzekutimit: {e}")
        return jsonify({"message": "Gabim me bazën e të dhënave", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
