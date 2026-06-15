from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg
from psycopg.rows import dict_row
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'dbname': 'proyecto_api',
    'user': 'postgres',
    'password': 'arries2016',
    'port': 5432
}

def get_db_connection():
    """Crea una conexión a PostgreSQL"""
    conn = psycopg.connect(**DB_CONFIG)
    return conn


@app.route('/formularios', methods=['POST'])
def crear_formulario():
    """Recibe datos del formulario y los inserta en la BD"""
    try:
        datos = request.get_json()

        # Validar campos obligatorios
        if not datos.get('nombre') or not datos.get('email') or not datos.get('asunto') or not datos.get('mensaje'):
            return jsonify({'error': 'Faltan campos obligatorios'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Insertar en la BD
        cur.execute("""
            INSERT INTO formularios (nombre, email, asunto, mensaje)
            VALUES (%s, %s, %s, %s)
            RETURNING id, nombre, email, asunto, mensaje, fecha_creacion;
        """, (
            datos['nombre'],
            datos['email'],
            datos['asunto'],
            datos['mensaje']
        ))

        resultado = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            'mensaje': 'Formulario enviado correctamente',
            'id': resultado[0],
            'nombre': resultado[1],
            'email': resultado[2],
            'asunto': resultado[3],
            'mensaje': resultado[4],
            'fecha_creacion': resultado[5].isoformat()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/formularios', methods=['GET'])
def obtener_formularios():
    """Devuelve todos los formularios"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)

        cur.execute(
            "SELECT * FROM formularios ORDER BY fecha_creacion DESC;"
        )

        formularios = cur.fetchall()

        cur.close()
        conn.close()

        for form in formularios:
            if isinstance(form['fecha_creacion'], datetime):
                form['fecha_creacion'] = form['fecha_creacion'].isoformat()

        return jsonify(formularios), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/formularios/<int:id>', methods=['GET'])
def obtener_formulario(id):
    """Devuelve un formulario por ID"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(row_factory=dict_row)

        cur.execute(
            "SELECT * FROM formularios WHERE id = %s;",
            (id,)
        )

        formulario = cur.fetchone()

        cur.close()
        conn.close()

        if not formulario:
            return jsonify({'error': 'Formulario no encontrado'}), 404

        if isinstance(formulario['fecha_creacion'], datetime):
            formulario['fecha_creacion'] = formulario['fecha_creacion'].isoformat()

        return jsonify(formulario), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)