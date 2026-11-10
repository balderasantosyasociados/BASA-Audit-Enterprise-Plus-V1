# -*- coding: utf-8 -*-

import os
import sqlite3
from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    Response
)

app = Flask(__name__)

# ============================================================================
# CONFIGURACION
# ============================================================================

DATABASE = os.path.join(os.getcwd(), "basa_audit.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            area TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM projects")

    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO projects
            (name, area, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (
                "Auditoría Financiera Q1",
                "Finanzas",
                "2026-01-15",
                "2026-03-30",
                "Activo"
            ),
            (
                "Revisión de Seguridad TI",
                "Tecnología",
                "2026-02-01",
                "2026-04-15",
                "Se necesita acción"
            )
        ])

    conn.commit()
    conn.close()


init_db()

# ============================================================================
# HTML PRINCIPAL
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">

<title>BASA Audit Enterprise Plus V1</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>

:root{
--primary:#0f172a;
--accent:#0284c7;
--bg:#f8fafc;
--card:#ffffff;
--border:#e2e8f0;
}

body{
margin:0;
padding:0;
background:var(--bg);
font-family:Segoe UI,sans-serif;
}

.header{
background:var(--primary);
color:white;
padding:15px 25px;
display:flex;
justify-content:space-between;
align-items:center;
}

.badge{
background:var(--accent);
padding:6px 12px;
border-radius:4px;
font-weight:bold;
}

.container{
max-width:1400px;
margin:auto;
padding:20px;
display:grid;
grid-template-columns:1fr 3fr;
gap:20px;
}

@media(max-width:900px){
.container{
grid-template-columns:1fr;
}
}

.card{
background:white;
border:1px solid var(--border);
border-radius:8px;
padding:20px;
}

.form-group{
margin-bottom:15px;
}

.form-group label{
display:block;
margin-bottom:4px;
font-weight:600;
}

.form-group input,
.form-group select{
width:100%;
padding:10px;
box-sizing:border-box;
}

.btn{
background:var(--accent);
color:white;
padding:10px;
border:none;
border-radius:4px;
cursor:pointer;
text-decoration:none;
display:inline-block;
}

.btn:hover{
opacity:.90;
}

.btn-secondary{
background:#64748b;
}

.btn-success{
background:#059669;
}

.btn-danger{
background:#dc2626;
}

.filter-bar{
display:flex;
gap:10px;
margin-bottom:20px;
align-items:end;
}

table{
width:100%;
border-collapse:collapse;
}

th,td{
padding:12px;
border-bottom:1px solid #ddd;
}

th{
background:#f1f5f9;
}

.status-badge{
padding:4px 10px;
border-radius:10px;
font-size:.8rem;
font-weight:bold;
}

.status-activo{
background:#dcfce7;
color:#15803d;
}

.status-accion{
background:#fee2e2;
color:#b91c1c;
}

.status-concluido{
background:#e2e8f0;
color:#334155;
}

.actions{
display:flex;
gap:5px;
}

</style>
</head>

<body>

<div class="header">
<h1>BASA Audit Enterprise Plus</h1>
<span class="badge">V2.0 Enterprise</span>
</div>

<div class="container">

<div class="card">

<h2>Nuevo Proyecto</h2>

<form action="{{ url_for('add_project') }}" method="POST">

<div class="form-group">
<label>Proyecto</label>
<input type="text" name="name" required>
</div>

<div class="form-group">
<label>Área</label>
<input type="text" name="area" required>
</div>

<div class="form-group">
<label>Fecha Inicio</label>
<input type="date" name="start_date" required>
</div>

<div class="form-group">
<label>Fecha Fin</label>
<input type="date" name="end_date" required>
</div>

<div class="form-group">
<label>Estado</label>
<select name="status">
<option value="Activo">Activo</option>
<option value="Se necesita acción">Se necesita acción</option>
</select>
</div>

<button class="btn" type="submit">
Registrar Proyecto
</button>

</form>

<br>

<a class="btn btn-secondary"
href="{{ url_for('export_csv', area=selected_area) }}">
Exportar CSV
</a>

</div>

<div class="card">

<h2>Panel de Auditorías</h2>

<form method="GET" class="filter-bar">

<div style="flex:1;">
<label>Área</label>

<select name="area">
<option value="">Todas</option>

{% for area in areas %}
<option value="{{ area }}"
{% if area == selected_area %}
selected
{% endif %}
>
{{ area }}
</option>
{% endfor %}

</select>

</div>

<button class="btn">
Filtrar
</button>

</form>

<table>

<thead>
<tr>
<th>Proyecto</th>
<th>Área</th>
<th>Inicio</th>
<th>Fin</th>
<th>Estado</th>
<th>Acciones</th>
</tr>
</thead>

<tbody>

{% for project in projects %}

<tr>

<td>{{ project["name"] }}</td>

<td>{{ project["area"] }}</td>

<td>{{ project["start_date"] }}</td>

<td>{{ project["end_date"] }}</td>

<td>

{% if project["status"] == "Activo" %}

<span class="status-badge status-activo">
Activo
</span>

{% elif project["status"] == "Concluido" %}

<span class="status-badge status-concluido">
Concluido
</span>

{% else %}

<span class="status-badge status-accion">
Se necesita acción
</span>

{% endif %}

</td>

<td>

<div class="actions">

<a class="btn btn-success"
href="{{ url_for('complete_project', project_id=project['id']) }}">
Concluir
</a>

<a class="btn"
href="{{ url_for('edit_project', project_id=project['id']) }}">
Editar
</a>

<a class="btn btn-danger"
href="{{ url_for('delete_project', project_id=project['id']) }}"
onclick="return confirm('¿Eliminar proyecto?')">
Eliminar
</a>

</div>

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

# ============================================================================
# HOME
# ============================================================================

@app.route("/")
def index():

    selected_area = request.args.get("area", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT area
        FROM projects
        ORDER BY area
    """)

    areas = [row[0] for row in cursor.fetchall()]

    if selected_area:
        cursor.execute("""
            SELECT *
            FROM projects
            WHERE area = ?
            ORDER BY id DESC
        """, (selected_area,))
    else:
        cursor.execute("""
            SELECT *
            FROM projects
            ORDER BY id DESC
        """)

    projects = cursor.fetchall()

    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        projects=projects,
        selected_area=selected_area,
        areas=areas
    )

# ============================================================================
# CREATE
# ============================================================================

@app.route("/add", methods=["POST"])
def add_project():

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO projects
        (
            name,
            area,
            start_date,
            end_date,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        request.form["name"],
        request.form["area"],
        request.form["start_date"],
        request.form["end_date"],
        request.form["status"]
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))

# ============================================================================
# UPDATE STATUS
# ============================================================================

@app.route("/complete/<int:project_id>")
def complete_project(project_id):

    conn = get_db_connection()

    conn.execute("""
        UPDATE projects
        SET status='Concluido'
        WHERE id=?
    """, (project_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))

# ============================================================================
# EDIT
# ============================================================================

@app.route("/edit/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):

    conn = get_db_connection()

    if request.method == "POST":

        conn.execute("""
            UPDATE projects
            SET
                name=?,
                area=?,
                start_date=?,
                end_date=?,
                status=?
            WHERE id=?
        """, (
            request.form["name"],
            request.form["area"],
            request.form["start_date"],
            request.form["end_date"],
            request.form["status"],
            project_id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    project = conn.execute(
        "SELECT * FROM projects WHERE id=?",
        (project_id,)
    ).fetchone()

    conn.close()

    return f"""
    <h2>Editar Proyecto</h2>

    <form method="post">

    <input name="name" value="{project['name']}" required><br><br>

    <input name="area" value="{project['area']}" required><br><br>

    <input type="date"
           name="start_date"
           value="{project['start_date']}"
           required><br><br>

    <input type="date"
           name="end_date"
           value="{project['end_date']}"
           required><br><br>

    <input name="status"
           value="{project['status']}"
           required><br><br>

    <button type="submit">
    Guardar
    </button>

    </form>
    """

# ============================================================================
# DELETE
# ============================================================================

@app.route("/delete/<int:project_id>")
def delete_project(project_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM projects WHERE id=?",
        (project_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))

# ============================================================================
# EXPORTACION CSV
# ============================================================================

@app.route("/export")
def export_csv():

    selected_area = request.args.get("area", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    if selected_area:
        cursor.execute("""
            SELECT *
            FROM projects
            WHERE area=?
            ORDER BY id
        """, (selected_area,))
    else:
        cursor.execute("""
            SELECT *
            FROM projects
            ORDER BY id
        """)

    rows = cursor.fetchall()

    conn.close()

    csv_data = "ID,Proyecto,Area,Inicio,Fin,Estado\n"

    for row in rows:
        csv_data += (
            f"{row['id']},"
            f"{row['name']},"
            f"{row['area']},"
            f"{row['start_date']},"
            f"{row['end_date']},"
            f"{row['status']}\n"
        )

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=basa_audit_projects.csv"
        }
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
