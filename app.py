# -*- coding: utf-8 -*-
import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Configuración de base de datos relacional para BASA Audit Enterprise Plus V1
DATABASE = 'basa_audit.db'

def init_db():
    """Inicializa la base de datos y crea la tabla de proyectos si no existe."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            area TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    # Inyectar datos iniciales de prueba si la base de datos está limpia
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO projects (name, area, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('Auditoría Financiera Q1', 'Finanzas', '2026-01-15', '2026-03-30', 'Activo'),
            ('Revisión de Seguridad TI', 'Tecnología', '2026-02-01', '2026-04-15', 'Se necesita acción')
        ])
    conn.commit()
    conn.close()

# Inicialización automatizada
init_db()

# =========================================================================
# INTERFAZ DE USUARIO INTEGRADA (HTML5 + CSS3 + JAVASCRIPT)
# =========================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>BASA Audit Enterprise Plus V1</title>
    <meta name="viewport" content="width=device-width, minimum-scale=1.0">
    <style>
        :root {
            --primary-color: #0f172a;
            --accent-color: #0284c7;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --border-color: #e2e8f0;
            --text-main: #1e293b;
        }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 0;
        }
        .header {
            background-color: var(--primary-color);
            color: white;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header h1 { margin: 0; font-size: 1.4rem; letter-spacing: 0.5px; }
        .badge {
            background-color: var(--accent-color);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; display: grid; grid-template-columns: 1fr 2fr; gap: 30px; }
        @media(max-width: 768px) { .container { grid-template-columns: 1fr; } }
        .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .card h2 { margin-top: 0; font-size: 1.2rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 8px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 6px; font-weight: 500; font-size: 0.9rem; }
        .form-group input, .form-group select { width: 100%; padding: 8px 12px; box-sizing: border-box; border: 1px solid var(--border-color); border-radius: 4px; font-size: 0.95rem; }
        .btn { background-color: var(--accent-color); color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: pointer; font-weight: 500; width: 100%; transition: background 0.2s; font-size: 1rem; }
        .btn:hover { background-color: #0369a1; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid var(--border-color); font-size: 0.95rem; }
        th { background-color: #f1f5f9; color: var(--primary-color); font-weight: 600; }
        .status-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
        .status-activo { background-color: #dcfce7; color: #15803d; }
        .status-accion { background-color: #fee2e2; color: #b91c1c; }
    </style>
</head>
<body>

    <div class="header">
        <h1>BASA Audit Enterprise Plus</h1>
        <span class="badge">V1.0.0 - Production</span>
    </div>

    <div class="container">
        <!-- Panel Izquierdo: Formulario de Registro -->
        <div class="card">
            <h2>Añadir Proyecto</h2>
            <form action="/add" method="POST">
                <div class="form-group">
                    <label>Nombre del Proyecto / Auditoría</label>
                    <input type="text" name="name" required placeholder="Ej: Control de Inventario">
                </div>
                <div class="form-group">
                    <label>Área Asignada</label>
                    <input type="text" name="area" required placeholder="Ej: Operaciones">
                </div>
                <div class="form-group">
                    <label>Fecha de Inicio</label>
                    <input type="date" name="start_date" required>
                </div>
                <div class="form-group">
                    <label>Fecha de Finalización</label>
                    <input type="date" name="end_date" required>
                </div>
                <div class="form-group">
                    <label>Estado del Flujo</label>
                    <select name="status">
                        <option value="Activo">Activo</option>
                        <option value="Se necesita acción">Se necesita acción</option>
                    </select>
                </div>
                <button type="submit" class="btn">Registrar en Panel</button>
            </form>
        </div>

        <!-- Panel Derecho: Visor de Plan de Auditoría -->
        <div class="card">
            <h2>Panel de Control: Plan de Auditoría</h2>
            <table>
                <thead>
                    <tr>
                        <th>Proyecto</th>
                        <th>Área</th>
                        <th>Vigencia (Inicio / Fin)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {% for project in projects %}
                    <tr>
                        <td><strong>{{ project[1] }}</strong></td>
                        <td>{{ project[2] }}</td>
                        <td>{{ project[3] }} ó {{ project[4] }}</td>
                        <td>
                            {% if project[5] == 'Activo' %}
                                <span class="status-badge status-activo">Activo</span>
                            {% else %}
                                <span class="status-badge status-accion">Se necesita acción</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

</body>
</html>
"""

# =========================================================================
# CONTROLADORES Y LOGICA DE RUTAS (API / BACKEND)
# =========================================================================
@app.route('/')
def index():
    """Lee el almacenamiento persistente de SQLite y renderiza el Dashboard."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, area, start_date, end_date, status FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, projects=projects)

@app.route('/add', methods=['POST'])
def add_project():
    """Captura las entradas del cliente y las registra en el sistema."""
    name = request.form.get('name')
    area = request.form.get('area')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    status = request.form.get('status')

    if name and area:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, area, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, area, start_date, end_date, status))
        conn.commit()
        conn.close()
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Lanzamiento del servidor web en el puerto de red local
    app.run(debug=True, port=5000)
