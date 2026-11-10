# -*- coding: utf-8 -*-
import sqlite3
import streamlit as str_web  # Usamos Streamlit para compatibilidad total online

# Configuración del entorno de página y diseño del sistema BASA
str_web.set_page_config(
    page_title="BASA Audit Enterprise Plus V1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATABASE = 'basa_audit.db'

def init_db():
    """Inicializa la base de datos relacional y crea los registros de prueba."""
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

# Iniciar la persistencia local de datos
init_db()

# =========================================================================
# HOJA DE ESTILOS INTEGRADA (CSS3 PARA RECREAR EL ENTORNO EMPRESARIAL)
# =========================================================================
str_web.markdown("""
    <style>
        /* Ocultar elementos nativos innecesarios de la plataforma */
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 1rem;}
        
        :root {
            --primary-color: #0f172a;
            --accent-color: #0284c7;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --border-color: #e2e8f0;
            --text-main: #1e293b;
        }
        .custom-header {
            background-color: var(--primary-color);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 6px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .custom-header h1 { margin: 0; font-size: 1.6rem; font-family: 'Segoe UI', sans-serif; color: white; }
        .custom-badge {
            background-color: var(--accent-color);
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        .card-title {
            font-size: 1.25rem;
            color: var(--primary-color);
            font-weight: 600;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 8px;
            margin-bottom: 15px;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            text-align: center;
        }
        .status-activo { background-color: #dcfce7; color: #15803d; }
        .status-accion { background-color: #fee2e2; color: #b91c1c; }
    </style>
    
    <div class="custom-header">
        <h1>BASA Audit Enterprise Plus</h1>
        <span class="custom-badge">V1.0.0 - Cloud Certified</span>
    </div>
""", unsafe_allow_html=True)

# Crear columnas en pantalla (Distribución 1:2 heredada del frontend original)
col_formulario, col_tabla = str_web.columns([1, 2], gap="large")

# =========================================================================
# COMPONENTE IZQUIERDO: FORMULARIO DE REGISTRO
# =========================================================================
with col_formulario:
    str_web.markdown('<div class="card-title">Añadir Proyecto</div>', unsafe_allow_html=True)
    
    with str_web.form("project_form", clear_on_submit=True):
        name = str_web.text_input("Nombre del Proyecto / Auditoría", placeholder="Ej: Control de Inventario")
        area = str_web.text_input("Área Asignada", placeholder="Ej: Operaciones")
        start_date = str_web.date_input("Fecha de Inicio")
        end_date = str_web.date_input("Fecha de Finalización")
        status = str_web.selectbox("Estado del Flujo", ["Activo", "Se necesita acción"])
        
        submit_btn = str_web.form_submit_button("Registrar en Panel", use_container_width=True)
        
        if submit_btn:
            if name and area:
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO projects (name, area, start_date, end_date, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, area, str(start_date), str(end_date), status))
                conn.commit()
                conn.close()
                str_web.toast("✅ Proyecto registrado con éxito")
            else:
                str_web.error("Por favor completa los campos obligatorios.")

# =========================================================================
# COMPONENTE DERECHO: VISOR DEL PLAN DE AUDITORÍA
# =========================================================================
with col_tabla:
    str_web.markdown('<div class="card-title">Panel de Control: Plan de Auditoría</div>', unsafe_allow_html=True)
    
    # Consultar datos actualizados de SQLite
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, area, start_date, end_date, status FROM projects ORDER BY id DESC")
    projects_list = cursor.fetchall()
    conn.close()
    
    # Dibujar la tabla estructurada con HTML limpio
    html_table = """
    <table style="width:100%; border-collapse: collapse; font-family: sans-serif;">
        <thead>
            <tr style="background-color: #f1f5f9; border-bottom: 2px solid #e2e8f0;">
                <th style="text-align: left; padding: 12px; color: #0f172a; font-weight: 600;">Proyecto</th>
                <th style="text-align: left; padding: 12px; color: #0f172a; font-weight: 600;">Área</th>
                <th style="text-align: left; padding: 12px; color: #0f172a; font-weight: 600;">Vigencia (Inicio / Fin)</th>
                <th style="text-align: left; padding: 12px; color: #0f172a; font-weight: 600;">Estado</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for row in projects_list:
        status_class = "status-activo" if row[4] == "Activo" else "status-accion"
        html_table += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 12px; color: #1e293b;"><strong>{row[0]}</strong></td>
                <td style="padding: 12px; color: #1e293b;">{row[1]}</td>
                <td style="padding: 12px; color: #1e293b;">{row[2]} ó {row[3]}</td>
                <td style="padding: 12px;">
                    <span class="status-badge {status_class}">{row[4]}</span>
                </td>
            </tr>
        """
        
    html_table += "</tbody></table>"
    str_web.markdown(html_table, unsafe_allow_html=True)
