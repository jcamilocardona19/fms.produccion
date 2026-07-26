"""
FMS.lab — Formación de Lotes en Sistemas de Manufactura Flexible
Universidad Tecnológica de Pereira — Producción III
Basado en: Medina, Cruz & Restrepo (2009)
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io, json, datetime, copy

st.set_page_config(
    page_title="FMS.lab — Formación de Lotes",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  ESTILOS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background-color:#f0f4f8;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a2332,#0d1520);}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
.metric-card{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:16px 20px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:8px;}
.metric-label{font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:#64748b;font-weight:600;margin-bottom:4px;}
.metric-value{font-size:1.3rem;font-weight:700;color:#1e3a5f;font-family:'IBM Plex Mono',monospace;}
.metric-value.ok{color:#16a34a;}.metric-value.bad{color:#dc2626;}.metric-value.warn{color:#d97706;}
.alert-ok{background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:12px 16px;color:#166534;margin:8px 0;}
.alert-warn{background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:12px 16px;color:#92400e;margin:8px 0;}
.alert-error{background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:12px 16px;color:#991b1b;margin:8px 0;}
.alert-info{background:#eff6ff;border:1px solid #93c5fd;border-radius:8px;padding:12px 16px;color:#1e40af;margin:8px 0;}
.section-title{font-size:1.4rem;font-weight:700;color:#1e3a5f;border-bottom:2px solid #2563eb;padding-bottom:8px;margin-bottom:20px;}
.lote-card{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:20px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,0.06);}
.lote-header{font-size:1rem;font-weight:700;color:#1e3a5f;margin-bottom:8px;}
.cuello{background:#fef2f2;border-left:4px solid #dc2626;border-radius:0 8px 8px 0;padding:8px 12px;font-size:0.85rem;color:#991b1b;margin:4px 0;}
.teoria-card{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:20px;margin-bottom:16px;}
.stButton>button{background:#2563eb;color:white;border:none;border-radius:8px;font-weight:600;}
.stButton>button:hover{background:#1d4ed8;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  ALGORITMO HEURÍSTICO — CORAZÓN DE LA APP
# ══════════════════════════════════════════════════════════════

def calcular_herramientas_lote(partes_lote, req_herramientas):
    """Retorna conjunto de herramientas necesarias para un conjunto de partes."""
    herrs = set()
    for p in partes_lote:
        herrs |= set(req_herramientas[p])
    return herrs

def calcular_slots_usados(herramientas_set, slots_herramientas):
    """Calcula slots totales ocupados por un conjunto de herramientas."""
    return sum(slots_herramientas.get(h, 1) for h in herramientas_set)

def calcular_carga_maquinas(partes_lote, tiempos, n_maquinas):
    """Calcula carga total por máquina para un conjunto de partes."""
    cargas = [0.0] * n_maquinas
    for p in partes_lote:
        for m in range(n_maquinas):
            cargas[m] += tiempos[p][m]
    return cargas

def calcular_desbalance(cargas):
    """Desbalance = max - min de cargas."""
    c = [x for x in cargas if x > 0]
    if not c: return 0
    return max(cargas) - min(cargas)

def heuristica_seleccion_partes(n_maquinas, n_partes, n_herramientas,
                                  capacidad_portaherramientas,
                                  tiempos, req_herramientas, slots_herramientas,
                                  nombres_partes, nombres_maquinas, nombres_herramientas):
    """
    Heurística de selección de partes para formación de lotes en FMS.
    Basada en: Medina, Cruz & Restrepo (2009).
    
    Criterio: en cada paso selecciona la parte que genera menor desbalance
    de carga entre estaciones al ser agregada al lote actual.
    """
    partes_disponibles = list(range(n_partes))
    lotes = []
    iteraciones_log = []

    while partes_disponibles:
        lote_actual = []
        herrs_lote = set()
        cargas_lote = [0.0] * n_maquinas
        log_lote = []

        # Intentar agregar partes al lote actual
        while True:
            candidatas = []
            for p in partes_disponibles:
                if p in lote_actual:
                    continue
                # Verificar factibilidad de herramientas
                herrs_candidata = set(req_herramientas[p])
                herrs_nuevas = herrs_lote | herrs_candidata
                slots_nuevos = calcular_slots_usados(herrs_nuevas, slots_herramientas)

                if slots_nuevos <= capacidad_portaherramientas:
                    # Calcular desbalance si se agrega esta parte
                    cargas_hipoteticas = [
                        cargas_lote[m] + tiempos[p][m]
                        for m in range(n_maquinas)
                    ]
                    desb = calcular_desbalance(cargas_hipoteticas)
                    carga_max = max(cargas_hipoteticas)
                    candidatas.append({
                        "parte": p,
                        "desbalance": desb,
                        "carga_max": carga_max,
                        "slots_usados": slots_nuevos,
                        "cargas": cargas_hipoteticas,
                    })

            if not candidatas:
                break  # No hay más partes factibles para este lote

            # Seleccionar parte con menor desbalance (criterio de la heurística)
            # Desempate: menor carga máxima
            candidatas.sort(key=lambda x: (x["desbalance"], x["carga_max"]))
            mejor = candidatas[0]
            p_sel = mejor["parte"]

            # Agregar al lote
            lote_actual.append(p_sel)
            herrs_lote |= set(req_herramientas[p_sel])
            cargas_lote = mejor["cargas"]
            partes_disponibles.remove(p_sel)

            log_lote.append({
                "paso": len(lote_actual),
                "parte_agregada": nombres_partes[p_sel],
                "desbalance": round(mejor["desbalance"], 3),
                "carga_max": round(mejor["carga_max"], 3),
                "slots_usados": mejor["slots_usados"],
                "cargas": [round(c, 3) for c in cargas_lote],
            })

        # Cerrar lote
        if lote_actual:
            cuello_idx = int(np.argmax(cargas_lote))
            lotes.append({
                "numero": len(lotes) + 1,
                "partes": lote_actual,
                "nombres_partes": [nombres_partes[p] for p in lote_actual],
                "herramientas": sorted(list(herrs_lote)),
                "nombres_herramientas": [nombres_herramientas[h] for h in sorted(list(herrs_lote))],
                "cargas": cargas_lote,
                "tiempo_lote": max(cargas_lote),
                "cuello_botella_idx": cuello_idx,
                "cuello_botella": nombres_maquinas[cuello_idx],
                "desbalance": calcular_desbalance(cargas_lote),
                "slots_usados": calcular_slots_usados(herrs_lote, slots_herramientas),
                "utilizacion": [c / max(cargas_lote) * 100 if max(cargas_lote) > 0 else 0 for c in cargas_lote],
                "log": log_lote,
            })
        iteraciones_log.extend(log_lote)

    return lotes, iteraciones_log

# ══════════════════════════════════════════════════════════════
#  GRÁFICAS
# ══════════════════════════════════════════════════════════════

def fig_to_img(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close(fig)
    return buf

def grafica_cargas_lote(lote, nombres_maquinas):
    """Gráfica de barras de carga por máquina para un lote."""
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')
    ax.set_facecolor('#f8fafc')
    cargas = lote["cargas"]
    n = len(cargas)
    idx = range(n)
    colores = ['#dc2626' if i == lote["cuello_botella_idx"] else '#2563eb' for i in range(n)]
    bars = ax.bar(idx, cargas, color=colores, edgecolor='white', linewidth=1.5, width=0.6)
    ax.axhline(lote["tiempo_lote"], color='#dc2626', linestyle='--', linewidth=1.5,
               label=f'Cuello de botella = {lote["tiempo_lote"]:.2f}')
    ax.set_xticks(list(idx))
    ax.set_xticklabels(nombres_maquinas, rotation=15, ha='right', fontsize=9)
    ax.set_ylabel('Carga (tiempo)', color='#1e3a5f', fontsize=10)
    ax.set_title(f'Lote {lote["numero"]} — Carga por Estación de Trabajo', fontweight='bold', color='#1e3a5f')
    ax.grid(True, axis='y', color='#e2e8f0', linestyle='--', alpha=0.8)
    for sp in ax.spines.values(): sp.set_edgecolor('#e2e8f0')
    ax.tick_params(colors='#64748b')
    for bar, val in zip(bars, cargas):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01*max(cargas),
                f'{val:.2f}', ha='center', va='bottom', fontsize=8, fontfamily='monospace')
    ax.legend(fontsize=9, framealpha=0.9)
    patch_cuello = mpatches.Patch(color='#dc2626', label='Cuello de botella')
    patch_normal = mpatches.Patch(color='#2563eb', label='Estación normal')
    ax.legend(handles=[patch_cuello, patch_normal], fontsize=8, framealpha=0.9)
    plt.tight_layout()
    return fig_to_img(fig)

def grafica_utilizacion_lote(lote, nombres_maquinas):
    """Gráfica de utilización por máquina."""
    fig, ax = plt.subplots(figsize=(10, 3.5), facecolor='white')
    ax.set_facecolor('#f8fafc')
    util = lote["utilizacion"]
    idx = range(len(util))
    colores = ['#dc2626' if i == lote["cuello_botella_idx"] else
               ('#16a34a' if util[i] >= 70 else '#d97706') for i in range(len(util))]
    bars = ax.barh(list(idx), util, color=colores, edgecolor='white', linewidth=1.2, height=0.5)
    ax.axvline(100, color='#dc2626', linestyle='--', linewidth=1.3, alpha=0.7)
    ax.set_yticks(list(idx))
    ax.set_yticklabels(nombres_maquinas, fontsize=9)
    ax.set_xlabel('Utilización (%)', color='#1e3a5f')
    ax.set_title(f'Lote {lote["numero"]} — Utilización de Máquinas', fontweight='bold', color='#1e3a5f')
    ax.set_xlim(0, 115)
    ax.grid(True, axis='x', color='#e2e8f0', linestyle='--', alpha=0.8)
    for sp in ax.spines.values(): sp.set_edgecolor('#e2e8f0')
    ax.tick_params(colors='#64748b')
    for bar, val in zip(bars, util):
        ax.text(val + 1, bar.get_y()+bar.get_height()/2, f'{val:.1f}%',
                va='center', fontsize=8, fontfamily='monospace')
    plt.tight_layout()
    return fig_to_img(fig)

def grafica_resumen_lotes(lotes, nombres_maquinas):
    """Gráfica comparativa de tiempos por lote."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), facecolor='white')

    # Gráfica 1: Tiempo por lote
    ax1 = axes[0]
    ax1.set_facecolor('#f8fafc')
    nums = [f"Lote {l['numero']}" for l in lotes]
    tiempos = [l['tiempo_lote'] for l in lotes]
    colores = ['#2563eb'] * len(lotes)
    bars = ax1.bar(range(len(lotes)), tiempos, color=colores, edgecolor='white', linewidth=1.2, width=0.6)
    ax1.set_xticks(range(len(lotes)))
    ax1.set_xticklabels(nums, rotation=15, ha='right', fontsize=9)
    ax1.set_ylabel('Tiempo del lote', color='#1e3a5f')
    ax1.set_title('Tiempo por Lote (cuello de botella)', fontweight='bold', color='#1e3a5f')
    ax1.grid(True, axis='y', color='#e2e8f0', linestyle='--', alpha=0.8)
    for sp in ax1.spines.values(): sp.set_edgecolor('#e2e8f0')
    ax1.tick_params(colors='#64748b')
    for bar, val in zip(bars, tiempos):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01*max(tiempos),
                 f'{val:.2f}', ha='center', va='bottom', fontsize=8, fontfamily='monospace')
    tiempo_total = sum(tiempos)
    ax1.axhline(tiempo_total/len(lotes), color='#d97706', linestyle='--', linewidth=1.3,
                label=f'Promedio = {tiempo_total/len(lotes):.2f}')
    ax1.legend(fontsize=8)

    # Gráfica 2: Desbalance por lote
    ax2 = axes[1]
    ax2.set_facecolor('#f8fafc')
    desb = [l['desbalance'] for l in lotes]
    colores2 = ['#dc2626' if d == max(desb) else '#16a34a' if d == min(desb) else '#d97706' for d in desb]
    bars2 = ax2.bar(range(len(lotes)), desb, color=colores2, edgecolor='white', linewidth=1.2, width=0.6)
    ax2.set_xticks(range(len(lotes)))
    ax2.set_xticklabels(nums, rotation=15, ha='right', fontsize=9)
    ax2.set_ylabel('Desbalance (max - min carga)', color='#1e3a5f')
    ax2.set_title('Desbalance por Lote', fontweight='bold', color='#1e3a5f')
    ax2.grid(True, axis='y', color='#e2e8f0', linestyle='--', alpha=0.8)
    for sp in ax2.spines.values(): sp.set_edgecolor('#e2e8f0')
    ax2.tick_params(colors='#64748b')
    for bar, val in zip(bars2, desb):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01*(max(desb)+0.01),
                 f'{val:.2f}', ha='center', va='bottom', fontsize=8, fontfamily='monospace')

    plt.tight_layout()
    return fig_to_img(fig)

def grafica_mapa_calor(lotes, nombres_maquinas):
    """Mapa de calor: carga por máquina por lote."""
    n_lotes = len(lotes)
    n_maq = len(nombres_maquinas)
    matriz = np.array([[lote['cargas'][m] for m in range(n_maq)] for lote in lotes])

    fig, ax = plt.subplots(figsize=(max(8, n_maq*1.2), max(4, n_lotes*0.8+1.5)), facecolor='white')
    im = ax.imshow(matriz, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(range(n_maq))
    ax.set_xticklabels(nombres_maquinas, rotation=30, ha='right', fontsize=9)
    ax.set_yticks(range(n_lotes))
    ax.set_yticklabels([f"Lote {l['numero']}" for l in lotes], fontsize=9)
    ax.set_title('Mapa de Calor — Carga por Máquina y Lote', fontweight='bold', color='#1e3a5f', pad=12)

    for i in range(n_lotes):
        for j in range(n_maq):
            val = matriz[i, j]
            color = 'white' if val > matriz.max()*0.6 else '#1e293b'
            ax.text(j, i, f'{val:.1f}', ha='center', va='center', fontsize=8,
                    color=color, fontfamily='monospace',
                    fontweight='bold' if j == lotes[i]['cuello_botella_idx'] else 'normal')

    plt.colorbar(im, ax=ax, label='Carga (tiempo)', shrink=0.8)
    plt.tight_layout()
    return fig_to_img(fig)

# ══════════════════════════════════════════════════════════════
#  DATOS DE EJEMPLO (del artículo)
# ══════════════════════════════════════════════════════════════

def datos_ejemplo():
    """Datos de ejemplo basados en el artículo de Medina, Cruz & Restrepo (2009)."""
    return {
        "n_maquinas": 4,
        "n_partes": 6,
        "n_herramientas": 8,
        "capacidad": 6,
        "nombres_maquinas": ["M1","M2","M3","M4"],
        "nombres_partes": ["P1","P2","P3","P4","P5","P6"],
        "nombres_herramientas": ["H1","H2","H3","H4","H5","H6","H7","H8"],
        "tiempos": [
            [3.0, 2.0, 0.0, 4.0],
            [0.0, 3.5, 2.5, 0.0],
            [2.0, 0.0, 3.0, 2.0],
            [4.0, 1.5, 0.0, 3.0],
            [0.0, 2.0, 4.0, 1.0],
            [3.0, 0.0, 2.0, 3.5],
        ],
        "req_herramientas": [
            [0,1,3],
            [1,2,4],
            [0,2,5],
            [3,4,6],
            [2,5,7],
            [0,6,7],
        ],
        "slots_herramientas": [1,1,1,1,1,1,1,1],
    }

# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════

def mostrar_header():
    col1, col2 = st.columns([1, 5])
    with col1:
        try: st.image("utp_logo.png", width=100)
        except: st.markdown("**UTP**")
    with col2:
        st.markdown("""
        <div style="padding:6px 0;">
        <div style="font-size:1.6rem;font-weight:700;color:#1e3a5f;">
        🏭 FMS.lab — Formación de Lotes de Fabricación
        </div>
        <div style="font-size:0.88rem;color:#64748b;margin-top:4px;">
        Universidad Tecnológica de Pereira &nbsp;·&nbsp; Producción III &nbsp;·&nbsp;
        Sistemas de Manufactura Flexible &nbsp;·&nbsp;
        Basado en Medina, Cruz & Restrepo (2009)
        </div></div>""", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:2px solid #2563eb;margin:8px 0 24px 0;'>",
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════

def sidebar_nav():
    with st.sidebar:
        try: st.image("utp_logo.png", width=120)
        except: pass
        st.markdown("---")
        st.markdown("### 🏭 Navegación")
        modulo = st.radio("", [
            "📖 Marco Teórico",
            "⚙️ Configurar FMS",
            "📊 Ejecutar Heurística",
            "📈 Resultados y Análisis",
            "📋 Reportes",
        ], label_visibility="collapsed")
        st.markdown("---")
        st.markdown("""
        <div style='font-size:0.75rem;color:#94a3b8;line-height:1.8;'>
        <b style='color:#bfdbfe;'>Referencia</b><br>
        Medina, Cruz & Restrepo<br>
        El Hombre y la Máquina<br>
        No. 32 · Enero-Junio 2009<br><br>
        <b style='color:#bfdbfe;'>Asignatura</b><br>
        Producción III<br>
        Ing. Industrial — UTP
        </div>
        """, unsafe_allow_html=True)
    return modulo

# ══════════════════════════════════════════════════════════════
#  MÓDULO 1 — MARCO TEÓRICO
# ══════════════════════════════════════════════════════════════

def modulo_teoria():
    st.markdown('<div class="section-title">📖 Marco Teórico — FMS y Formación de Lotes</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "¿Qué es un FMS?", "El Problema", "La Heurística", "Temas de Producción III"
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="teoria-card">
            <h4>🏭 Sistema de Manufactura Flexible (FMS)</h4>
            Un FMS es un sistema de producción automatizado compuesto por:
            <ul>
            <li><b>Estaciones de trabajo CNC</b> reprogramables</li>
            <li><b>Sistema automático</b> de cambio y entrega de herramientas</li>
            <li><b>Manejo automático</b> de materiales entre estaciones</li>
            <li><b>Control central</b> que coordina todo el sistema</li>
            </ul>
            Permite fabricar gran variedad de partes de manera simultánea.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="teoria-card">
            <h4>⚙️ Portaherramientas</h4>
            Cada máquina del FMS tiene un <b>portaherramientas</b> con capacidad
            limitada de <b>slots</b>. Si la suma de herramientas requeridas por
            todas las partes supera esta capacidad, <b>no se pueden fabricar todas
            a la vez</b> y se deben formar lotes.
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="teoria-card">
            <h4>📦 Lote de Fabricación</h4>
            Un lote consta de una cantidad específica de cada tipo de parte que
            se fabricarán en un período determinado. Los lotes se producen
            <b>secuencialmente</b>:
            <ol>
            <li>Se configura el sistema para el lote</li>
            <li>Se cargan todas las herramientas necesarias</li>
            <li>Se fabrican todas las partes del lote</li>
            <li>Se prepara el sistema para el siguiente lote</li>
            </ol>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="teoria-card">
            <h4>🔴 Cuello de Botella</h4>
            En cada lote, la <b>estación de trabajo con mayor carga</b> determina
            el tiempo total del lote. Esta es el cuello de botella que limita la
            producción. El tiempo del lote = tiempo del cuello de botella.
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### El Problema de Selección de Partes")
        st.markdown("""
        <div class="alert-info">
        📌 <b>Problema central:</b> Dado un conjunto de partes a fabricar y una
        capacidad limitada de portaherramientas, ¿cómo agrupar las partes en lotes
        para <b>minimizar el tiempo total de producción</b>?
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Variables del problema")
        st.dataframe(pd.DataFrame({
            "Variable": ["P", "M", "T", "tᵢⱼ", "aᵢₖ", "Cₘ", "sₖ"],
            "Descripción": [
                "Conjunto de partes a fabricar",
                "Conjunto de máquinas del FMS",
                "Conjunto de herramientas disponibles",
                "Tiempo de procesamiento de parte i en máquina j",
                "1 si parte i requiere herramienta k, 0 si no",
                "Capacidad del portaherramientas (slots)",
                "Slots que ocupa la herramienta k",
            ],
            "Tipo": ["Entrada","Entrada","Entrada","Entrada","Entrada","Parámetro","Parámetro"],
        }), hide_index=True, use_container_width=True)

        st.markdown("#### Restricciones")
        restricciones = [
            ("Capacidad", "Σ slots(herramientas del lote) ≤ Cₘ", "No se pueden cargar más herramientas que slots disponibles"),
            ("Factibilidad", "Todas las herramientas del lote deben estar cargadas al inicio", "El sistema se configura una vez por lote"),
            ("Cobertura", "Cada parte aparece en exactamente un lote", "Todas las partes deben ser fabricadas"),
            ("Secuencia", "Los lotes se producen uno tras otro", "No hay producción paralela entre lotes"),
        ]
        st.dataframe(pd.DataFrame(restricciones,
                     columns=["Restricción","Condición","Explicación"]),
                     hide_index=True, use_container_width=True)

    with tab3:
        st.markdown("### Heurística de Selección de Partes")
        st.markdown("""
        <div class="alert-info">
        📌 La heurística es un algoritmo <b>constructivo</b> que forma los lotes
        uno a uno, seleccionando en cada paso la parte que genera el
        <b>menor desbalance de carga</b> entre las estaciones de trabajo.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Criterio de selección")
        st.markdown("""
        ```
        Desbalance = max(carga_j) − min(carga_j)   ∀ j ∈ Máquinas

        Se selecciona la parte i* que minimiza el Desbalance al ser agregada.
        ```
        """)

        st.markdown("#### Pseudocódigo del algoritmo")
        st.code("""
INICIO
  partes_disponibles ← {todas las partes}
  lotes ← []

  MIENTRAS partes_disponibles ≠ ∅:
    lote_actual ← {}
    herramientas_lote ← {}
    cargas ← [0, 0, ..., 0]   ← una por máquina

    MIENTRAS existan partes factibles:
      Para cada parte i en partes_disponibles:
        Si (herramientas(i) ∪ herramientas_lote) ≤ Capacidad:
          Calcular Desbalance(cargas + tiempos(i))
          Guardar como candidata

      Si no hay candidatas → SALIR del while interno

      Seleccionar i* = argmin(Desbalance)
      Agregar i* al lote_actual
      Actualizar herramientas_lote y cargas
      Eliminar i* de partes_disponibles

    Registrar lote_actual con:
      - Cuello de botella = máquina con max(cargas)
      - Tiempo del lote = max(cargas)
    Agregar lote_actual a lotes

  Tiempo total = Σ Tiempo(lote)
FIN
        """, language="python")

        st.markdown("#### Función objetivo")
        st.markdown("""
        ```
        Minimizar:  Z = Σ max(Carga_j(l))   ∀ lote l
        ```
        Minimizar la suma de tiempos de todos los lotes equivale a minimizar
        el tiempo total de producción del sistema.
        """)

    with tab4:
        st.markdown("### Temas de Producción III presentes en el artículo")
        temas = [
            ("Formación de lotes", "✅ Central", "Es el problema principal del artículo"),
            ("Sistemas Flexibles de Manufactura", "✅ Central", "Contexto tecnológico del problema"),
            ("Cuello de botella", "✅ Central", "Determina el tiempo de cada lote"),
            ("Capacidad instalada", "✅ Alta", "Restricción de portaherramientas"),
            ("Balanceo de carga", "✅ Alta", "Criterio principal de la heurística"),
            ("Teoría de Restricciones (TOC)", "✅ Alta", "El cuello de botella limita todo el sistema"),
            ("Secuenciación de producción", "✅ Media", "Los lotes se producen en secuencia"),
            ("Programación de producción", "✅ Media", "Asignación de partes a períodos"),
            ("Utilización de máquinas", "✅ Media", "Se calcula y analiza por estación"),
            ("Optimización heurística", "✅ Alta", "Heurística constructiva de selección"),
            ("Investigación de Operaciones", "✅ Media", "Modelo matemático de fondo"),
            ("Eficiencia del sistema", "✅ Media", "Medida a través del desbalance"),
        ]
        st.dataframe(pd.DataFrame(temas,
                     columns=["Tema","Presencia","Descripción"]),
                     hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 2 — CONFIGURAR FMS
# ══════════════════════════════════════════════════════════════

def modulo_configurar():
    st.markdown('<div class="section-title">⚙️ Configuración del Sistema FMS</div>',
                unsafe_allow_html=True)

    # Cargar ejemplo
    if st.button("📂 Cargar datos de ejemplo (Medina et al., 2009)", type="primary"):
        st.session_state["fms_config"] = datos_ejemplo()
        st.success("✅ Datos de ejemplo cargados correctamente.")

    st.markdown("---")

    # Configuración básica
    st.markdown("### 1. Parámetros generales del FMS")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        n_maq = st.number_input("N° de máquinas", min_value=2, max_value=15, value=4)
    with c2:
        n_par = st.number_input("N° de tipos de partes", min_value=2, max_value=20, value=6)
    with c3:
        n_herr = st.number_input("N° de herramientas", min_value=2, max_value=30, value=8)
    with c4:
        cap = st.number_input("Capacidad portaherramientas (slots)", min_value=2, max_value=50, value=6)

    st.markdown("---")
    st.markdown("### 2. Nombres")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Máquinas:**")
        nombres_maq = [st.text_input(f"Máquina {i+1}", value=f"M{i+1}", key=f"nm_{i}") for i in range(int(n_maq))]
    with c2:
        st.markdown("**Partes:**")
        nombres_par = [st.text_input(f"Parte {i+1}", value=f"P{i+1}", key=f"np_{i}") for i in range(int(n_par))]
    with c3:
        st.markdown("**Herramientas:**")
        nombres_herr = [st.text_input(f"Herramienta {i+1}", value=f"H{i+1}", key=f"nh_{i}") for i in range(int(n_herr))]

    st.markdown("---")
    st.markdown("### 3. Tiempos de procesamiento")
    st.markdown("*Ingresa el tiempo que tarda cada parte en cada máquina. Usa 0 si la parte no requiere esa máquina.*")

    cfg = st.session_state.get("fms_config", {})
    tiempos_prev = cfg.get("tiempos", [[0.0]*int(n_maq)]*int(n_par))

    tiempos = []
    for i in range(int(n_par)):
        cols = st.columns([2] + [1]*int(n_maq))
        with cols[0]:
            st.markdown(f"<div style='padding:8px 0;font-weight:600;color:#1e3a5f;'>{nombres_par[i]}</div>",
                        unsafe_allow_html=True)
        fila = []
        for j in range(int(n_maq)):
            prev = tiempos_prev[i][j] if i < len(tiempos_prev) and j < len(tiempos_prev[i]) else 0.0
            with cols[j+1]:
                val = st.number_input(nombres_maq[j], min_value=0.0, value=float(prev),
                                      step=0.5, key=f"t_{i}_{j}", label_visibility="visible")
                fila.append(val)
        tiempos.append(fila)

    st.markdown("---")
    st.markdown("### 4. Requerimientos de herramientas por parte")
    st.markdown("*Marca qué herramientas necesita cada parte.*")

    req_prev = cfg.get("req_herramientas", [[] for _ in range(int(n_par))])
    req_herramientas = []
    for i in range(int(n_par)):
        prev_set = set(req_prev[i]) if i < len(req_prev) else set()
        cols = st.columns([2] + [1]*int(n_herr))
        with cols[0]:
            st.markdown(f"<div style='padding:4px 0;font-weight:600;color:#1e3a5f;'>{nombres_par[i]}</div>",
                        unsafe_allow_html=True)
        req_fila = []
        for k in range(int(n_herr)):
            with cols[k+1]:
                sel = st.checkbox(nombres_herr[k], value=(k in prev_set),
                                  key=f"r_{i}_{k}", label_visibility="visible")
                if sel:
                    req_fila.append(k)
        req_herramientas.append(req_fila)

    st.markdown("---")
    st.markdown("### 5. Slots por herramienta")
    st.markdown("*Slots que ocupa cada herramienta en el portaherramientas (por defecto 1).*")
    slots_prev = cfg.get("slots_herramientas", [1]*int(n_herr))
    cols_s = st.columns(min(int(n_herr), 8))
    slots_herr = []
    for k in range(int(n_herr)):
        prev_s = slots_prev[k] if k < len(slots_prev) else 1
        with cols_s[k % 8]:
            s = st.number_input(nombres_herr[k], min_value=1, max_value=10,
                                value=int(prev_s), key=f"s_{k}")
            slots_herr.append(s)

    st.markdown("---")
    if st.button("💾 Guardar configuración del FMS", type="primary"):
        config = {
            "n_maquinas": int(n_maq),
            "n_partes": int(n_par),
            "n_herramientas": int(n_herr),
            "capacidad": int(cap),
            "nombres_maquinas": nombres_maq,
            "nombres_partes": nombres_par,
            "nombres_herramientas": nombres_herr,
            "tiempos": tiempos,
            "req_herramientas": req_herramientas,
            "slots_herramientas": slots_herr,
        }
        st.session_state["fms_config"] = config
        st.session_state["lotes"] = None
        st.success("✅ Configuración guardada. Ve al módulo 'Ejecutar Heurística'.")

    # Previsualización
    if "fms_config" in st.session_state:
        cfg = st.session_state["fms_config"]
        st.markdown("---")
        st.markdown("### Vista previa de la configuración guardada")
        c1, c2, c3, c4 = st.columns(4)
        for col, lbl, val in [(c1,"Máquinas",cfg['n_maquinas']),(c2,"Partes",cfg['n_partes']),
                               (c3,"Herramientas",cfg['n_herramientas']),(c4,"Capacidad (slots)",cfg['capacidad'])]:
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div>'
                            f'<div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

        st.markdown("#### Matriz de tiempos de procesamiento")
        df_t = pd.DataFrame(cfg["tiempos"],
                            index=cfg["nombres_partes"],
                            columns=cfg["nombres_maquinas"])
        st.dataframe(df_t, use_container_width=True)

        st.markdown("#### Requerimientos de herramientas")
        req_display = []
        for i, p in enumerate(cfg["nombres_partes"]):
            herrs = [cfg["nombres_herramientas"][k] for k in cfg["req_herramientas"][i]]
            slots = sum(cfg["slots_herramientas"][k] for k in cfg["req_herramientas"][i])
            req_display.append({"Parte": p, "Herramientas requeridas": ", ".join(herrs), "Slots totales": slots})
        df_r = pd.DataFrame(req_display)
        st.dataframe(df_r, hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 3 — EJECUTAR HEURÍSTICA
# ══════════════════════════════════════════════════════════════

def modulo_ejecutar():
    st.markdown('<div class="section-title">📊 Ejecutar Heurística de Selección de Partes</div>',
                unsafe_allow_html=True)

    if "fms_config" not in st.session_state:
        st.markdown('<div class="alert-warn">⚠️ Primero debes configurar el FMS en el módulo anterior.</div>',
                    unsafe_allow_html=True)
        return

    cfg = st.session_state["fms_config"]

    # Resumen de config
    c1, c2, c3, c4 = st.columns(4)
    for col, lbl, val in [(c1,"Máquinas",cfg['n_maquinas']),(c2,"Partes",cfg['n_partes']),
                           (c3,"Herramientas",cfg['n_herramientas']),(c4,"Cap. portaherramientas",cfg['capacidad'])]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div>'
                        f'<div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Verificación de factibilidad")

    # Verificar si alguna parte sola excede la capacidad
    problemas = []
    for i, p in enumerate(cfg["nombres_partes"]):
        slots_p = sum(cfg["slots_herramientas"][k] for k in cfg["req_herramientas"][i])
        if slots_p > cfg["capacidad"]:
            problemas.append(f"Parte {p} requiere {slots_p} slots — excede la capacidad de {cfg['capacidad']}")

    if problemas:
        for prob in problemas:
            st.markdown(f'<div class="alert-error">🚨 {prob}</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-error">❌ El problema no tiene solución factible con la capacidad actual.</div>',
                    unsafe_allow_html=True)
        return
    else:
        st.markdown('<div class="alert-ok">✅ Todos los requerimientos son factibles con la capacidad configurada.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Ejecutar algoritmo")
    st.markdown("""
    <div class="alert-info">
    ℹ️ La heurística evaluará todas las partes disponibles en cada paso y seleccionará
    la que genere el <b>menor desbalance de carga</b> entre las estaciones de trabajo,
    respetando la restricción de capacidad del portaherramientas.
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶ Ejecutar Heurística de Selección de Partes", type="primary", use_container_width=True):
        with st.spinner("Ejecutando heurística..."):
            lotes, log = heuristica_seleccion_partes(
                cfg["n_maquinas"], cfg["n_partes"], cfg["n_herramientas"],
                cfg["capacidad"], cfg["tiempos"], cfg["req_herramientas"],
                cfg["slots_herramientas"], cfg["nombres_partes"],
                cfg["nombres_maquinas"], cfg["nombres_herramientas"]
            )
        st.session_state["lotes"] = lotes
        st.session_state["log"] = log
        st.success(f"✅ Heurística ejecutada. Se formaron {len(lotes)} lote(s).")
        st.rerun()

    # Mostrar traza de ejecución si hay resultados
    if st.session_state.get("lotes"):
        lotes = st.session_state["lotes"]
        st.markdown("---")
        st.markdown("### Traza de ejecución paso a paso")

        for lote in lotes:
            with st.expander(f"📦 Lote {lote['numero']} — {len(lote['partes'])} parte(s) — Tiempo: {lote['tiempo_lote']:.2f}"):
                df_log = pd.DataFrame(lote["log"])
                if not df_log.empty:
                    cargas_cols = pd.DataFrame(df_log["cargas"].tolist(),
                                               columns=cfg["nombres_maquinas"])
                    df_display = pd.concat([
                        df_log[["paso","parte_agregada","desbalance","carga_max","slots_usados"]],
                        cargas_cols
                    ], axis=1)
                    df_display.columns = ["Paso","Parte agregada","Desbalance","Carga máx","Slots usados"] + cfg["nombres_maquinas"]
                    st.dataframe(df_display, hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 4 — RESULTADOS
# ══════════════════════════════════════════════════════════════

def modulo_resultados():
    st.markdown('<div class="section-title">📈 Resultados y Análisis del FMS</div>',
                unsafe_allow_html=True)

    if not st.session_state.get("lotes"):
        st.markdown('<div class="alert-warn">⚠️ Primero ejecuta la heurística en el módulo anterior.</div>',
                    unsafe_allow_html=True)
        return

    lotes = st.session_state["lotes"]
    cfg   = st.session_state["fms_config"]
    nombres_maquinas = cfg["nombres_maquinas"]

    tiempo_total = sum(l["tiempo_lote"] for l in lotes)
    n_lotes = len(lotes)
    cuello_global = max(lotes, key=lambda l: l["tiempo_lote"])
    desb_promedio = np.mean([l["desbalance"] for l in lotes])

    # KPIs globales
    st.markdown("### KPIs Globales del Sistema")
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, lbl, val, cls in [
        (c1, "Lotes formados",    str(n_lotes),                 ""),
        (c2, "Tiempo total",      f"{tiempo_total:.2f}",        "warn"),
        (c3, "Tiempo promedio/lote", f"{tiempo_total/n_lotes:.2f}", ""),
        (c4, "Cuello de botella global", cuello_global["cuello_botella"], "bad"),
        (c5, "Desbalance promedio", f"{desb_promedio:.2f}",     "warn"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div>'
                        f'<div class="metric-value {cls}">{val}</div></div>',
                        unsafe_allow_html=True)

    st.markdown("---")

    # Resumen de lotes
    st.markdown("### Resumen de lotes formados")
    resumen = []
    for l in lotes:
        resumen.append({
            "Lote": f"Lote {l['numero']}",
            "Partes": ", ".join(l["nombres_partes"]),
            "Herramientas": ", ".join(l["nombres_herramientas"]),
            "Slots usados": l["slots_usados"],
            "Cuello de botella": l["cuello_botella"],
            "Tiempo lote": round(l["tiempo_lote"], 3),
            "Desbalance": round(l["desbalance"], 3),
        })
    df_res = pd.DataFrame(resumen)
    st.dataframe(df_res, hide_index=True, use_container_width=True)

    st.markdown("---")

    # Gráficas de resumen
    st.markdown("### Análisis comparativo de lotes")
    st.image(grafica_resumen_lotes(lotes, nombres_maquinas), use_column_width=True)

    st.markdown("### Mapa de calor — Carga por máquina y lote")
    st.image(grafica_mapa_calor(lotes, nombres_maquinas), use_column_width=True)

    st.markdown("---")

    # Detalle por lote
    st.markdown("### Análisis detallado por lote")
    for lote in lotes:
        with st.expander(f"📦 Lote {lote['numero']} — Partes: {', '.join(lote['nombres_partes'])} — ⏱ {lote['tiempo_lote']:.2f}", expanded=True):
            c1, c2 = st.columns(2)

            with c1:
                st.markdown(f"""
                <div class="lote-card">
                <div class="lote-header">Información del Lote {lote['numero']}</div>
                <b>Partes:</b> {", ".join(lote['nombres_partes'])}<br>
                <b>Herramientas:</b> {", ".join(lote['nombres_herramientas'])}<br>
                <b>Slots usados:</b> {lote['slots_usados']} / {cfg['capacidad']}<br>
                <b>Tiempo del lote:</b> {lote['tiempo_lote']:.3f}<br>
                <b>Desbalance:</b> {lote['desbalance']:.3f}
                <div class="cuello">
                🔴 Cuello de botella: <b>{lote['cuello_botella']}</b>
                (Carga: {lote['cargas'][lote['cuello_botella_idx']]:.3f})
                </div>
                </div>
                """, unsafe_allow_html=True)

                # Tabla de cargas
                df_cargas = pd.DataFrame({
                    "Máquina": nombres_maquinas,
                    "Carga": [round(c, 3) for c in lote["cargas"]],
                    "Utilización (%)": [round(u, 1) for u in lote["utilizacion"]],
                    "¿Cuello?": ["🔴 SÍ" if i == lote["cuello_botella_idx"] else "🟢 No"
                                 for i in range(len(nombres_maquinas))],
                })
                st.dataframe(df_cargas, hide_index=True, use_container_width=True)

            with c2:
                st.image(grafica_cargas_lote(lote, nombres_maquinas), use_column_width=True)

            st.image(grafica_utilizacion_lote(lote, nombres_maquinas), use_column_width=True)

    st.markdown("---")

    # Recomendaciones automáticas
    st.markdown("### 💡 Recomendaciones del sistema")

    lote_max_desb = max(lotes, key=lambda l: l["desbalance"])
    lote_min_util = min(lotes, key=lambda l: min(l["utilizacion"]))

    recomendaciones = [
        f"🔴 El **Lote {cuello_global['numero']}** tiene el mayor tiempo ({cuello_global['tiempo_lote']:.2f}). "
        f"Priorizar la reducción de carga en **{cuello_global['cuello_botella']}** para mejorar el tiempo total.",

        f"⚠️ El **Lote {lote_max_desb['numero']}** tiene el mayor desbalance ({lote_max_desb['desbalance']:.2f}). "
        f"Redistribuir operaciones entre estaciones para equilibrar la carga.",

        f"📊 El tiempo total de producción es **{tiempo_total:.2f}** unidades para {cfg['n_partes']} tipos de partes "
        f"en {n_lotes} lote(s).",

        f"🔧 La capacidad del portaherramientas ({cfg['capacidad']} slots) limitó la formación de lotes. "
        f"Aumentarla podría reducir el número de lotes y el tiempo total.",
    ]

    for rec in recomendaciones:
        st.markdown(f'<div class="alert-info">{rec}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 5 — REPORTES
# ══════════════════════════════════════════════════════════════

def modulo_reportes():
    st.markdown('<div class="section-title">📋 Reportes y Exportación</div>',
                unsafe_allow_html=True)

    if not st.session_state.get("lotes"):
        st.markdown('<div class="alert-warn">⚠️ Primero ejecuta la heurística para generar reportes.</div>',
                    unsafe_allow_html=True)
        return

    lotes = st.session_state["lotes"]
    cfg   = st.session_state["fms_config"]
    ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M")

    st.markdown("### Exportar datos")

    tab1, tab2, tab3 = st.tabs(["📦 Resumen de Lotes", "📊 Cargas por Máquina", "🔗 Asignación de Herramientas"])

    with tab1:
        rows = []
        for l in lotes:
            rows.append({
                "Lote": l["numero"],
                "Partes": ", ".join(l["nombres_partes"]),
                "N_Partes": len(l["partes"]),
                "Herramientas": ", ".join(l["nombres_herramientas"]),
                "Slots_Usados": l["slots_usados"],
                "Capacidad": cfg["capacidad"],
                "Cuello_de_Botella": l["cuello_botella"],
                "Tiempo_Lote": round(l["tiempo_lote"], 4),
                "Desbalance": round(l["desbalance"], 4),
            })
        df1 = pd.DataFrame(rows)
        st.dataframe(df1, hide_index=True, use_container_width=True)
        csv1 = df1.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇️ Descargar resumen de lotes (.csv)", csv1,
                           f"fms_lotes_{ts}.csv", "text/csv", type="primary")

    with tab2:
        rows2 = []
        for l in lotes:
            for m_idx, m in enumerate(cfg["nombres_maquinas"]):
                rows2.append({
                    "Lote": l["numero"],
                    "Maquina": m,
                    "Carga": round(l["cargas"][m_idx], 4),
                    "Utilizacion_%": round(l["utilizacion"][m_idx], 2),
                    "Es_Cuello": "SÍ" if m_idx == l["cuello_botella_idx"] else "No",
                    "Tiempo_Lote": round(l["tiempo_lote"], 4),
                })
        df2 = pd.DataFrame(rows2)
        st.dataframe(df2, hide_index=True, use_container_width=True)
        csv2 = df2.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇️ Descargar cargas por máquina (.csv)", csv2,
                           f"fms_cargas_{ts}.csv", "text/csv", type="primary")

    with tab3:
        rows3 = []
        for l in lotes:
            for p_idx in l["partes"]:
                for h_idx in cfg["req_herramientas"][p_idx]:
                    rows3.append({
                        "Lote": l["numero"],
                        "Parte": cfg["nombres_partes"][p_idx],
                        "Herramienta": cfg["nombres_herramientas"][h_idx],
                        "Slots": cfg["slots_herramientas"][h_idx],
                    })
        df3 = pd.DataFrame(rows3)
        st.dataframe(df3, hide_index=True, use_container_width=True)
        csv3 = df3.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇️ Descargar asignación de herramientas (.csv)", csv3,
                           f"fms_herramientas_{ts}.csv", "text/csv", type="primary")

    st.markdown("---")
    st.markdown("### Exportar configuración completa del FMS")
    config_json = json.dumps(st.session_state["fms_config"], indent=2, ensure_ascii=False)
    st.download_button("⬇️ Descargar configuración FMS (.json)", config_json.encode("utf-8"),
                       f"fms_config_{ts}.json", "application/json")
    st.markdown('<div class="alert-info">💡 Guarda el archivo JSON para cargar esta configuración en el futuro.</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Cargar configuración guardada")
    uploaded = st.file_uploader("Subir archivo de configuración (.json)", type=["json"])
    if uploaded:
        try:
            config_cargada = json.load(uploaded)
            st.session_state["fms_config"] = config_cargada
            st.session_state["lotes"] = None
            st.success("✅ Configuración cargada. Ve a 'Ejecutar Heurística' para re-ejecutar.")
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

# ══════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    # Inicializar session state
    if "fms_config" not in st.session_state:
        st.session_state["fms_config"] = None
    if "lotes" not in st.session_state:
        st.session_state["lotes"] = None
    if "log" not in st.session_state:
        st.session_state["log"] = None

    mostrar_header()
    mod = sidebar_nav()

    if   "Marco"       in mod: modulo_teoria()
    elif "Configurar"  in mod: modulo_configurar()
    elif "Ejecutar"    in mod: modulo_ejecutar()
    elif "Resultados"  in mod: modulo_resultados()
    elif "Reportes"    in mod: modulo_reportes()

if __name__ == "__main__":
    main()
