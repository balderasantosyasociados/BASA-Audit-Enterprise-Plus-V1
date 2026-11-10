# -*- coding: utf-8 -*-
import sqlite3
import streamlit as st

# Configuración estricta de página para producción
st.set_page_config(
    page_title="BASA Audit Enterprise Plus V1",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Base de datos relacional local
DATABASE = 'basa_audit.db'

def init_db():
    """Inicializa la base de datos relacional y crea la tabla si no existe."""
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
    if cursor.fetchone() == 0:
        cursor.executemany('''
            INSERT INTO projects (name, area, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('Auditoría Financiera Q1', 'Finanzas', '2026-01-15', '2026-03-30', 'Activo'),
            ('Revisión de Seguridad TI', 'Tecnología', '2026-02-01', '2026-04-15', 'Se necesita acción')
        ])
    conn.commit()
    conn.close()

# Iniciar persistencia de datos
init_db()

# =========================================================================
# LÓGICA DE PROCESAMIENTO DE ACCIONES (ELIMINAR / CONCLUIR)
# =========================================================================
if "action_to_do" in st.session_state:
    action = st.session_state.action_to_do
    project_id = st.session_state.project_id_target
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if action == "concluir":
        cursor.execute("UPDATE projects SET status = 'Concluido' WHERE id = ?", (project_id,))
        st.toast("🎯 Proyecto marcado como Concluido")
    elif action == "eliminar":
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        st.toast("🗑️ Proyecto eliminado permanentemente")
    conn.commit()
    conn.close()
    
    # Limpiar estado para evitar bucles de ejecución
    del st.session_state.action_to_do
    del st.session_state.project_id_target
    st.rerun()

# Estilos corporativos CSS3 inyectados de forma segura (Sin usar F-Strings para evitar errores)
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 1rem;}
        .custom-header {
            background-color: #0f172a;
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 6px;
            margin-bottom: 25px;
        }
        .custom-header h1 { margin: 0; font-size: 1.6rem; color: white !important; }
        .custom-badge {
            background-color: #0284c7;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: bold;
            color: white;
        }
        .card-title {
            font-size: 1.25rem;
            color: #0f172a;
            font-weight: 600;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }
    </style>
    
    <div class="custom-header">
        <h1>BASA Audit Enterprise Plus</h1>
        <span class="custom-badge">V1.1.0 - Full Enterprise</span>
    </div>
""", unsafe_allow_html=True)

# =========================================================================
# MENÚ LATERAL: SISTEMA DE FILTROS Y EXPORTACIÓN
# =========================================================================
with st.sidebar:
    st.markdown('<div class="card-title">🔍 Filtros y Herramientas</div>', unsafe_allow_html=True)
    
    # Obtener lista de áreas únicas de la BD para el buscador
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT area FROM projects")
    areas_disponibles = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    filtro_area = st.selectbox("Filtrar por Área:", ["Todas"] + areas_disponibles)
    buscar_nombre = st.text_input("Buscar por Nombre:", placeholder="Ej: Financiera")
    
    st.markdown("---")
    st.markdown('<div class="card-title">📦 Exportar Datos</div>', unsafe_allow_html=True)
    
    # Generar la data lista para descargar en formato CSV (Excel)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, area, start_date, end_date, status FROM projects ORDER BY id DESC")
    all_data = cursor.fetchall()
    conn.close()
    
    csv_content = "Proyecto,Area,Fecha Inicio,Fecha Fin,Estado\n"
    for row in all_data:
        csv_content += '"' + row[0] + '","' + row[1] + '","' + row[2] + '","' + row[3] + '","' + row[4] + '"\n'
        
    st.download_button(
        label="📥 Descargar a Excel (CSV)",
        data=csv_content.encode('utf-8-sig'),
        file_name="Plan_Auditoria_BASA.csv",
        mime="text/csv",
        use_container_width=True
    )

# Layout principal: Distribución en columnas (1:2)
col_formulario, col_tabla = st.columns([1, 2], gap="large")

# =========================================================================
# COMPONENTE IZQUIERDO: FORMULARIO DE REGISTRO
# =========================================================================
with col_formulario:
    st.markdown('<div class="card-title">Añadir Proyecto</div>', unsafe_allow_html=True)
    
    with st.form("project_form", clear_on_submit=True):
        name = st.text_input("Nombre del Proyecto / Auditoría", placeholder="Ej: Control de Inventario")
        area = st.text_input("Área Asignada", placeholder="Ej: Operaciones")
        start_date = st.date_input("Fecha de Inicio")
        end_date = st.date_input("Fecha de Finalización")
        status = st.selectbox("Estado del Flujo", ["Activo", "Se necesita acción"])
        
        submit_btn = st.form_submit_button("Registrar en Panel", use_container_width=True)
        
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
                st.toast("✅ Registro completado exitosamente")
                st.rerun()
            else:
                st.error("Campos obligatorios incompletos.")

# =========================================================================
# COMPONENTE DERECHO: VISOR DINÁMICO CON ACCIONES
# =========================================================================
with col_tabla:
    st.markdown('<div class="card-title">Panel de Control: Plan de Auditoría</div>', unsafe_allow_html=True)
    
    # Consulta SQL dinámica basada en los filtros
    query = "SELECT id, name, area, start_date, end_date, status FROM projects WHERE 1=1"
    params = []
    
    if filtro_area != "Todas":
        query += " AND area = ?"
        params.append(filtro_area)
    if buscar_nombre:
        query += " AND name LIKE ?"
        params.append("%" + buscar_nombre + "%")
        
    query += " ORDER BY id DESC"
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    projects_list = cursor.fetchall()
    conn.close()
    
    if not projects_list:
        st.info("No se encontraron auditorías que coincidan con los filtros aplicados.")
    else:
        # Cabecera estática de la tabla corporativa
        st.markdown("""
        <table style="width:100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 10px;">
            <thead>
                <tr style="background-color: #f1f5f9; border-bottom: 2px solid #e2e8f0;">
                    <th style="text-align: left; padding: 12px; color: #0f172a; font-weight: 600; width: 30%;">Proyecto</th>
                    <th style="text-align: left; padding: 12px; color: #0f172a; font-weight: 600; width: 20%;">Área</th>
                    <th style="text-align: left; padding: 12px; color: #0f172a; font-weight: 600; width: 25%;">Vigencia</th>
                    <th style="text-align: left; padding: 12px; color: #0f172a; font-weight: 600; width: 25%;">Estado</th>
                </tr>
            </thead>
        </table>
        """, unsafe_allow_html=True)
        
        # Iteración segura utilizando concatenación e inyección HTML básica
        for row in projects_list:
            p_id, p_name, p_area, p_start, p_end, p_status = row
            
            # Definir color del Badge según estado
            if p_status == "Activo":
                b_color, t_color = "#dcfce7", "#15803d"
            elif p_status == "Concluido":
                b_color, t_color = "#e2e8f0", "#475569"
            else:
                b_color, t_color = "#fee2e2", "#b91c1c"
                
            # Renderizado HTML libre de f-string complejo
            html_row = f"""
            <table style="width:100%; border-collapse: collapse; font-family: sans-serif; margin-top: -10px;">
                <tr style="border-bottom: 1px solid #e2e8f0; background: white;">
                    <td style="padding: 12px; color: #1e293b; width: 30%;"><strong>{p_name}</strong></td>
                    <td style="padding: 12px; color: #1e293b; width: 20%;">{p_area}</td>
                    <td style="padding: 12px; color: #1e293b; width: 25%; font-size: 0.85rem;">{p_start} / {p_end}</td>
                    <td style="padding: 12px; width: 25%;">
