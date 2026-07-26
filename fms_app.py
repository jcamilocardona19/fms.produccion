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
import io, json, datetime

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

/* SIDEBAR */
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#0f2440 0%,#1a3a5c 60%,#0d1e35 100%);
    border-right:1px solid #1e3a5f;
}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
[data-testid="stSidebar"] .stRadio label{
    color:#e2e8f0!important;
    padding:6px 0;
}

/* CARDS */
.metric-card{
    background:white;
    border:1px solid #e2e8f0;
    border-radius:12px;
    padding:18px 20px;
    text-align:center;
    box-shadow:0 2px 8px rgba(0,0,0,0.07);
    margin-bottom:8px;
    transition:transform 0.2s;
}
.metric-card:hover{transform:translateY(-2px);}
.metric-label{font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;color:#64748b;font-weight:600;margin-bottom:6px;}
.metric-value{font-size:1.4rem;font-weight:700;color:#1e3a5f;font-family:'IBM Plex Mono',monospace;}
.metric-value.ok{color:#16a34a;}
.metric-value.bad{color:#dc2626;}
.metric-value.warn{color:#d97706;}

/* ALERTS */
.alert-ok{background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:12px 16px;color:#166534;margin:8px 0;}
.alert-warn{background:#fffbeb;border:1px solid #fcd34d;border-radius:10px;padding:12px 16px;color:#92400e;margin:8px 0;}
.alert-error{background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:12px 16px;color:#991b1b;margin:8px 0;}
.alert-info{background:#eff6ff;border:1px solid #93c5fd;border-radius:10px;padding:12px 16px;color:#1e40af;margin:8px 0;}

/* SECTION TITLE */
.section-title{
    font-size:1.4rem;font-weight:700;color:#1e3a5f;
    border-bottom:3px solid #2563eb;
    padding-bottom:10px;margin-bottom:24px;
    letter-spacing:-0.3px;
}

/* TEORIA CARDS */
.teoria-card{
    background:white;
    border:1px solid #e2e8f0;
    border-radius:12px;
    padding:20px;
    margin-bottom:16px;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
    line-height:1.7;
}
.teoria-card h4{color:#1e3a5f;margin-bottom:10px;font-size:1rem;border-left:3px solid #2563eb;padding-left:8px;}

/* LOTE CARDS */
.lote-card{
    background:white;
    border:1px solid #e2e8f0;
    border-radius:12px;
    padding:20px;
    margin-bottom:16px;
    box-shadow:0 2px 8px rgba(0,0,0,0.06);
}
.lote-header{font-size:1.05rem;font-weight:700;color:#1e3a5f;margin-bottom:10px;display:flex;align-items:center;gap:8px;}
.cuello-badge{
    background:#fef2f2;border:1px solid #fca5a5;
    border-radius:8px;padding:8px 14px;
    font-size:0.88rem;color:#991b1b;
    margin:8px 0;display:inline-block;
}

/* FORMULA BOX */
.formula-box{
    background:#f1f5f9;
    border-left:4px solid #2563eb;
    border-radius:0 10px 10px 0;
    padding:14px 18px;
    font-family:'IBM Plex Mono',monospace;
    font-size:0.88rem;color:#1e3a5f;
    margin:12px 0;line-height:2;
}

/* REFERENCE CARD */
.ref-card{
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-radius:8px;
    padding:14px 18px;
    margin-bottom:10px;
    font-size:0.88rem;
    color:#374151;
    line-height:1.8;
    border-left:3px solid #2563eb;
}

/* BUTTONS */
.stButton>button{
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    color:white;border:none;border-radius:10px;
    font-weight:600;font-size:0.95rem;
    padding:10px 24px;
    box-shadow:0 2px 8px rgba(37,99,235,0.3);
    transition:all 0.2s;
}
.stButton>button:hover{
    background:linear-gradient(135deg,#1d4ed8,#1e40af);
    box-shadow:0 4px 12px rgba(37,99,235,0.4);
    transform:translateY(-1px);
}

/* BANNER */
.banner-utp{
    background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 60%,#1e40af 100%);
    border-radius:14px;
    padding:28px 32px;
    margin-bottom:28px;
    color:white;
    box-shadow:0 4px 20px rgba(37,99,235,0.25);
}
.banner-title{font-size:1.7rem;font-weight:700;letter-spacing:-0.5px;margin-bottom:4px;}
.banner-sub{font-size:0.9rem;color:#bfdbfe;line-height:1.6;}

/* STEP BADGE */
.step-badge{
    display:inline-flex;align-items:center;justify-content:center;
    background:#2563eb;color:white;
    border-radius:50%;width:28px;height:28px;
    font-size:0.8rem;font-weight:700;
    margin-right:8px;flex-shrink:0;
}

/* GRADIENT DIVIDER */
.grad-divider{
    height:3px;
    background:linear-gradient(90deg,#2563eb,#7c3aed,#2563eb);
    border:none;border-radius:2px;
    margin:24px 0;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  ALGORITMO HEURÍSTICO
# ══════════════════════════════════════════════════════════════

def calc_slots(herrs, slots_h):
    return sum(slots_h[h] for h in herrs)

def calc_desb(cargas):
    c = [x for x in cargas if x >= 0]
    if not c: return 0
    return max(cargas) - min(cargas)

def heuristica_fms(n_maq, n_par, capacidad, tiempos,
                   req_herr, slots_herr, nom_par, nom_maq, nom_herr):
    partes_disp = list(range(n_par))
    lotes = []

    while partes_disp:
        lote_act = []
        herrs_lote = set()
        cargas = [0.0] * n_maq
        log_lote = []

        while True:
            candidatas = []
            for p in partes_disp:
                herrs_nueva = herrs_lote | set(req_herr[p])
                if calc_slots(herrs_nueva, slots_herr) <= capacidad:
                    c_hip = [cargas[m] + tiempos[p][m] for m in range(n_maq)]
                    desb = calc_desb(c_hip)
                    candidatas.append({
                        "parte": p,
                        "desbalance": round(desb, 4),
                        "carga_max": round(max(c_hip), 4),
                        "slots": calc_slots(herrs_nueva, slots_herr),
                        "cargas": c_hip,
                    })

            if not candidatas:
                break

            candidatas.sort(key=lambda x: (x["desbalance"], x["carga_max"]))
            mejor = candidatas[0]
            p_sel = mejor["parte"]
            lote_act.append(p_sel)
            herrs_lote |= set(req_herr[p_sel])
            cargas = mejor["cargas"]
            partes_disp.remove(p_sel)

            log_lote.append({
                "Paso": len(lote_act),
                "Parte agregada": nom_par[p_sel],
                "Desbalance": round(mejor["desbalance"], 3),
                "Carga máx": round(mejor["carga_max"], 3),
                "Slots usados": mejor["slots"],
                **{nom_maq[m]: round(cargas[m], 3) for m in range(n_maq)},
            })

        if lote_act:
            cuello_idx = int(np.argmax(cargas))
            herrs_sorted = sorted(list(herrs_lote))
            lotes.append({
                "numero": len(lotes) + 1,
                "partes": lote_act,
                "nombres_partes": [nom_par[p] for p in lote_act],
                "herramientas": herrs_sorted,
                "nombres_herramientas": [nom_herr[h] for h in herrs_sorted],
                "cargas": cargas,
                "tiempo_lote": max(cargas),
                "cuello_idx": cuello_idx,
                "cuello_botella": nom_maq[cuello_idx],
                "desbalance": calc_desb(cargas),
                "slots_usados": calc_slots(herrs_lote, slots_herr),
                "utilizacion": [c/max(cargas)*100 if max(cargas) > 0 else 0 for c in cargas],
                "log": log_lote,
            })

    return lotes

# ══════════════════════════════════════════════════════════════
#  GRÁFICAS
# ══════════════════════════════════════════════════════════════

PALETA = {
    "azul":    "#2563eb",
    "rojo":    "#dc2626",
    "verde":   "#16a34a",
    "naranja": "#d97706",
    "morado":  "#7c3aed",
    "gris":    "#64748b",
    "fondo":   "#f8fafc",
    "borde":   "#e2e8f0",
}

def fig_to_img(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=140, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close(fig)
    return buf

def grafica_cargas(lote, nombres_maq):
    fig, ax = plt.subplots(figsize=(10, 4.5), facecolor='white')
    ax.set_facecolor(PALETA["fondo"])
    n = len(lote["cargas"])
    idx = range(n)
    colores = [PALETA["rojo"] if i == lote["cuello_idx"] else PALETA["azul"] for i in range(n)]
    bars = ax.bar(idx, lote["cargas"], color=colores, edgecolor='white',
                  linewidth=2, width=0.6, zorder=3)
    ax.axhline(lote["tiempo_lote"], color=PALETA["rojo"], linestyle='--',
               linewidth=1.8, alpha=0.8, label=f'Cuello de botella = {lote["tiempo_lote"]:.2f}', zorder=2)
    ax.set_xticks(list(idx))
    ax.set_xticklabels(nombres_maq, fontsize=10, color='#374151')
    ax.set_ylabel('Carga (tiempo)', color='#1e3a5f', fontsize=11)
    ax.set_title(f'Lote {lote["numero"]} — Carga por Estación de Trabajo',
                 fontweight='bold', color='#1e3a5f', fontsize=12, pad=12)
    ax.grid(True, axis='y', color=PALETA["borde"], linestyle='--', alpha=0.8, zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for sp in ['left','bottom']: ax.spines[sp].set_edgecolor(PALETA["borde"])
    ax.tick_params(colors='#64748b')
    for bar, val in zip(bars, lote["cargas"]):
        ax.text(bar.get_x()+bar.get_width()/2,
                bar.get_height()+max(lote["cargas"])*0.02,
                f'{val:.2f}', ha='center', va='bottom',
                fontsize=9, fontfamily='monospace', fontweight='bold',
                color=PALETA["rojo"] if bar.get_height()==lote["tiempo_lote"] else '#374151')
    p1 = mpatches.Patch(color=PALETA["rojo"], label='Cuello de botella')
    p2 = mpatches.Patch(color=PALETA["azul"], label='Estación normal')
    ax.legend(handles=[p1, p2], fontsize=9, framealpha=0.95,
              facecolor='white', edgecolor=PALETA["borde"])
    plt.tight_layout()
    return fig_to_img(fig)

def grafica_utilizacion(lote, nombres_maq):
    fig, ax = plt.subplots(figsize=(10, 3.5), facecolor='white')
    ax.set_facecolor(PALETA["fondo"])
    util = lote["utilizacion"]
    idx = range(len(util))
    colores = [PALETA["rojo"] if i == lote["cuello_idx"] else
               (PALETA["verde"] if util[i] >= 70 else PALETA["naranja"])
               for i in range(len(util))]
    bars = ax.barh(list(idx), util, color=colores, edgecolor='white',
                   linewidth=1.5, height=0.5, zorder=3)
    ax.axvline(100, color=PALETA["rojo"], linestyle='--', linewidth=1.3, alpha=0.6, zorder=2)
    ax.set_yticks(list(idx))
    ax.set_yticklabels(nombres_maq, fontsize=10, color='#374151')
    ax.set_xlabel('Utilización (%)', color='#1e3a5f', fontsize=10)
    ax.set_title(f'Lote {lote["numero"]} — Utilización de Máquinas',
                 fontweight='bold', color='#1e3a5f', fontsize=12, pad=10)
    ax.set_xlim(0, 120)
    ax.grid(True, axis='x', color=PALETA["borde"], linestyle='--', alpha=0.8, zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for sp in ['left','bottom']: ax.spines[sp].set_edgecolor(PALETA["borde"])
    for bar, val in zip(bars, util):
        ax.text(val+1.5, bar.get_y()+bar.get_height()/2,
                f'{val:.1f}%', va='center', fontsize=9,
                fontfamily='monospace', fontweight='bold', color='#374151')
    plt.tight_layout()
    return fig_to_img(fig)

def grafica_resumen(lotes, nombres_maq):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor='white')
    fig.suptitle('Análisis Global del Sistema FMS', fontweight='bold',
                 color='#1e3a5f', fontsize=13, y=1.01)

    # Tiempo por lote
    ax1 = axes[0]
    ax1.set_facecolor(PALETA["fondo"])
    nums = [f"Lote {l['numero']}" for l in lotes]
    tiempos = [l['tiempo_lote'] for l in lotes]
    colores = [PALETA["rojo"] if t == max(tiempos) else PALETA["azul"] for t in tiempos]
    bars = ax1.bar(range(len(lotes)), tiempos, color=colores,
                   edgecolor='white', linewidth=2, width=0.6, zorder=3)
    prom = sum(tiempos)/len(tiempos)
    ax1.axhline(prom, color=PALETA["naranja"], linestyle='--',
                linewidth=1.5, label=f'Promedio = {prom:.2f}', zorder=2)
    ax1.set_xticks(range(len(lotes)))
    ax1.set_xticklabels(nums, rotation=15, ha='right', fontsize=9)
    ax1.set_ylabel('Tiempo del lote', color='#1e3a5f', fontsize=10)
    ax1.set_title('Tiempo por Lote\n(determinado por el cuello de botella)',
                  fontweight='bold', color='#1e3a5f', fontsize=10)
    ax1.grid(True, axis='y', color=PALETA["borde"], linestyle='--', alpha=0.8, zorder=1)
    ax1.spines['top'].set_visible(False); ax1.spines['right'].set_visible(False)
    for bar, val in zip(bars, tiempos):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(tiempos)*0.015,
                 f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontfamily='monospace')
    ax1.legend(fontsize=9, framealpha=0.95, facecolor='white', edgecolor=PALETA["borde"])

    # Desbalance por lote
    ax2 = axes[1]
    ax2.set_facecolor(PALETA["fondo"])
    desb = [l['desbalance'] for l in lotes]
    col2 = [PALETA["rojo"] if d == max(desb) else
            (PALETA["verde"] if d == min(desb) else PALETA["naranja"]) for d in desb]
    bars2 = ax2.bar(range(len(lotes)), desb, color=col2,
                    edgecolor='white', linewidth=2, width=0.6, zorder=3)
    ax2.set_xticks(range(len(lotes)))
    ax2.set_xticklabels(nums, rotation=15, ha='right', fontsize=9)
    ax2.set_ylabel('Desbalance (max − min carga)', color='#1e3a5f', fontsize=10)
    ax2.set_title('Desbalance por Lote\n(menor = mejor balanceo)',
                  fontweight='bold', color='#1e3a5f', fontsize=10)
    ax2.grid(True, axis='y', color=PALETA["borde"], linestyle='--', alpha=0.8, zorder=1)
    ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
    for bar, val in zip(bars2, desb):
        ax2.text(bar.get_x()+bar.get_width()/2,
                 bar.get_height()+(max(desb)+0.01)*0.015 if max(desb) > 0 else 0.01,
                 f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontfamily='monospace')
    p1 = mpatches.Patch(color=PALETA["rojo"], label='Mayor desbalance')
    p2 = mpatches.Patch(color=PALETA["verde"], label='Menor desbalance')
    ax2.legend(handles=[p1, p2], fontsize=9, framealpha=0.95,
               facecolor='white', edgecolor=PALETA["borde"])

    plt.tight_layout()
    return fig_to_img(fig)

def grafica_calor(lotes, nombres_maq):
    n_l = len(lotes); n_m = len(nombres_maq)
    matriz = np.array([[l['cargas'][m] for m in range(n_m)] for l in lotes])
    fig, ax = plt.subplots(figsize=(max(9, n_m*1.4), max(4, n_l*0.9+2)), facecolor='white')
    im = ax.imshow(matriz, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(range(n_m)); ax.set_xticklabels(nombres_maq, rotation=30, ha='right', fontsize=10)
    ax.set_yticks(range(n_l)); ax.set_yticklabels([f"Lote {l['numero']}" for l in lotes], fontsize=10)
    ax.set_title('Mapa de Calor — Carga por Máquina y Lote\n(rojo = mayor carga)',
                 fontweight='bold', color='#1e3a5f', fontsize=12, pad=14)
    for i in range(n_l):
        for j in range(n_m):
            val = matriz[i, j]
            color = 'white' if val > matriz.max()*0.6 else '#1e293b'
            fw = 'bold' if j == lotes[i]['cuello_idx'] else 'normal'
            ax.text(j, i, f'{val:.1f}', ha='center', va='center',
                    fontsize=9, color=color, fontfamily='monospace', fontweight=fw)
    plt.colorbar(im, ax=ax, label='Carga (tiempo)', shrink=0.8)
    plt.tight_layout()
    return fig_to_img(fig)

# ══════════════════════════════════════════════════════════════
#  DATOS DE EJEMPLO
# ══════════════════════════════════════════════════════════════

def datos_ejemplo():
    return {
        "n_maquinas": 4, "n_partes": 6, "n_herramientas": 8, "capacidad": 6,
        "nombres_maquinas": ["M1","M2","M3","M4"],
        "nombres_partes": ["P1","P2","P3","P4","P5","P6"],
        "nombres_herramientas": ["H1","H2","H3","H4","H5","H6","H7","H8"],
        "tiempos": [[3.0,2.0,0.0,4.0],[0.0,3.5,2.5,0.0],[2.0,0.0,3.0,2.0],
                    [4.0,1.5,0.0,3.0],[0.0,2.0,4.0,1.0],[3.0,0.0,2.0,3.5]],
        "req_herramientas": [[0,1,3],[1,2,4],[0,2,5],[3,4,6],[2,5,7],[0,6,7]],
        "slots_herramientas": [1,1,1,1,1,1,1,1],
    }

# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════

def mostrar_header():
    col1, col2 = st.columns([1, 6])
    with col1:
        try:
            st.image("utp_logo.png", width=105)
        except:
            st.markdown("**UTP**")
    with col2:
        st.markdown("""
        <div class="banner-utp">
            <div class="banner-title">🏭 FMS.lab — Formación de Lotes de Fabricación</div>
            <div class="banner-sub">
            Universidad Tecnológica de Pereira &nbsp;·&nbsp; Ingeniería Industrial &nbsp;·&nbsp; Producción III<br>
            Heurística de Selección de Partes en Sistemas de Manufactura Flexible (FMS)<br>
            <span style="opacity:0.8;font-size:0.85rem;">
            Basado en: Medina Varela, Cruz Trejos & Restrepo Correa (2009)
            </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════

def sidebar_nav():
    with st.sidebar:
        try:
            st.image("utp_logo.png", width=130)
        except:
            pass
        st.markdown("---")
        st.markdown("### 🏭 Navegación")
        modulo = st.radio("", [
            "📖 Marco Teórico",
            "⚙️ Configurar FMS",
            "▶ Ejecutar Heurística",
            "📈 Resultados y Análisis",
            "📋 Reportes",
            "📚 Referencias",
        ], label_visibility="collapsed")
        st.markdown("---")
        st.markdown("""
        <div style='font-size:0.76rem;color:#94a3b8;line-height:1.9;'>
        <b style='color:#bfdbfe;'>Referencia principal</b><br>
        Medina, Cruz & Restrepo<br>
        <i>El Hombre y la Máquina</i><br>
        No. 32 · Ene–Jun 2009<br>
        UTP — Pereira, Colombia<br><br>
        <b style='color:#bfdbfe;'>Asignatura</b><br>
        Producción III<br>
        Ing. Industrial — UTP<br><br>
        <b style='color:#bfdbfe;'>Tema</b><br>
        Sistemas Flexibles de<br>
        Manufactura (FMS)<br>
        Formación de Lotes
        </div>
        """, unsafe_allow_html=True)
    return modulo

# ══════════════════════════════════════════════════════════════
#  MÓDULO 1 — MARCO TEÓRICO
# ══════════════════════════════════════════════════════════════

def modulo_teoria():
    st.markdown('<div class="section-title">📖 Marco Teórico — FMS y Formación de Lotes</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🏭 ¿Qué es un FMS?","📦 El Problema","🧮 La Heurística","🎓 Producción III"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="teoria-card">
            <h4>🏭 Sistema de Manufactura Flexible (FMS)</h4>
            Un FMS es un sistema de producción automatizado con cuatro características clave:
            <ul>
            <li><b>Estaciones CNC</b> reprogramables automáticamente</li>
            <li><b>Cambio automático</b> de herramientas entre operaciones</li>
            <li><b>Transporte automático</b> de materiales entre estaciones</li>
            <li><b>Control central</b> que coordina todo el sistema</li>
            </ul>
            Permite fabricar <b>gran variedad de partes simultáneamente</b> sin intervención manual.
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="teoria-card">
            <h4>⚙️ Portaherramientas — La restricción clave</h4>
            Cada máquina tiene un <b>portaherramientas con capacidad limitada</b> (slots).
            Si las herramientas requeridas por todas las partes superan esa capacidad,
            <b>no se pueden fabricar todas a la vez</b> → se forman <b>lotes</b>.
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="teoria-card">
            <h4>📦 Lote de Fabricación</h4>
            Un lote es un subconjunto de partes que se fabrican juntas en un período:
            <ol>
            <li>Configurar el sistema para el lote</li>
            <li>Cargar <b>todas las herramientas</b> necesarias al inicio</li>
            <li>Fabricar todas las partes del lote</li>
            <li>Preparar el sistema para el siguiente lote</li>
            </ol>
            Los lotes se producen <b>secuencialmente</b>, uno tras otro.
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="teoria-card">
            <h4>🔴 Cuello de Botella</h4>
            La <b>estación con mayor carga</b> determina el tiempo total del lote.
            Es el recurso que limita la producción (Teoría de Restricciones — TOC).
            <br><br>
            <b>Tiempo del lote = Tiempo del cuello de botella</b>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### Dos contextos del FMS según Medina et al. (2009)")
        st.dataframe(pd.DataFrame({
            "Contexto": ["Portaherramientas insuficiente","Portaherramientas suficiente"],
            "Condición": ["Slots disponibles < Herramientas requeridas","Slots disponibles ≥ Herramientas requeridas"],
            "Acción": ["Formar lotes de fabricación","Iniciar producción directamente"],
            "Este módulo": ["✅ Aplica","❌ No aplica"],
        }), hide_index=True, use_container_width=True)

    with tab2:
        st.markdown('<div class="alert-info">📌 <b>Problema central:</b> Dado un conjunto de partes y capacidad limitada de portaherramientas, ¿cómo agruparlas en lotes para <b>minimizar el tiempo total de producción</b>?</div>', unsafe_allow_html=True)
        st.markdown("#### Variables del modelo")
        st.dataframe(pd.DataFrame({
            "Variable": ["P","M","T","tᵢⱼ","aᵢₖ","Cₘ","sₖ"],
            "Descripción": ["Conjunto de partes a fabricar","Conjunto de máquinas del FMS",
                            "Conjunto de herramientas disponibles",
                            "Tiempo de procesamiento de parte i en máquina j",
                            "1 si parte i requiere herramienta k; 0 si no",
                            "Capacidad del portaherramientas (slots)",
                            "Slots que ocupa la herramienta k"],
            "Tipo": ["Entrada","Entrada","Entrada","Entrada","Entrada","Parámetro","Parámetro"],
        }), hide_index=True, use_container_width=True)
        st.markdown("#### Restricciones")
        st.dataframe(pd.DataFrame({
            "Restricción": ["Capacidad","Factibilidad","Cobertura","Secuencia"],
            "Condición": ["Σ slots(herramientas lote) ≤ Cₘ",
                          "Todas las herramientas del lote cargadas al inicio",
                          "Cada parte en exactamente un lote",
                          "Lotes producidos secuencialmente"],
            "Explicación": ["No exceder el portaherramientas",
                            "Configuración única por lote",
                            "Ninguna parte se omite",
                            "Sin producción paralela entre lotes"],
        }), hide_index=True, use_container_width=True)
        st.markdown("#### Función objetivo")
        st.markdown("""
        <div class="formula-box">
        Minimizar:  Z = Σ max(Carga_j(l))   ∀ lote l<br><br>
        Donde:  Carga_j(l) = Σ tᵢⱼ   ∀ parte i en lote l
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="alert-info">📌 La heurística es un algoritmo <b>constructivo</b> que forma lotes seleccionando en cada paso la parte que genera el <b>menor desbalance de carga</b> entre las estaciones, respetando la capacidad del portaherramientas.</div>', unsafe_allow_html=True)
        st.markdown("#### Criterio de selección")
        st.markdown("""
        <div class="formula-box">
        Desbalance = max(Carga_j) − min(Carga_j)   ∀ j ∈ Máquinas<br><br>
        Se selecciona la parte i* = argmin(Desbalance al agregar i)
        </div>
        """, unsafe_allow_html=True)
        st.markdown("#### Pseudocódigo")
        st.code("""
INICIO
  partes_disponibles ← {P₁, P₂, ..., Pₙ}
  lotes ← []

  MIENTRAS partes_disponibles ≠ ∅:
    lote_actual ← {}
    herramientas_lote ← {}
    cargas[j] ← 0   ∀ j ∈ Máquinas

    MIENTRAS existan partes factibles:
      PARA cada parte i en partes_disponibles:
        SI slots(herramientas(i) ∪ herramientas_lote) ≤ Cₘ:
          c_hip[j] ← cargas[j] + tᵢⱼ   ∀ j
          Desbalance_i ← max(c_hip) − min(c_hip)
          Agregar i como candidata

      SI candidatas = ∅ → SALIR del while interno

      i* ← parte con menor Desbalance_i
      Agregar i* a lote_actual
      Actualizar herramientas_lote y cargas
      Eliminar i* de partes_disponibles

    Cuello_de_botella ← j con max(cargas[j])
    Tiempo_lote ← max(cargas[j])
    Agregar lote_actual a lotes

  Tiempo_total ← Σ Tiempo_lote
FIN
        """, language="python")

    with tab4:
        st.markdown("### Temas de Producción III presentes en el artículo")
        temas = [
            ("Formación de lotes","✅ Central","Problema principal del artículo"),
            ("Sistemas Flexibles de Manufactura","✅ Central","Contexto tecnológico completo"),
            ("Cuello de botella","✅ Central","Determina el tiempo de cada lote"),
            ("Teoría de Restricciones (TOC)","✅ Alta","El cuello de botella limita el sistema"),
            ("Capacidad instalada","✅ Alta","Restricción de portaherramientas"),
            ("Balanceo de carga","✅ Alta","Criterio principal de la heurística"),
            ("Secuenciación de producción","✅ Media","Los lotes se producen en secuencia"),
            ("Utilización de máquinas","✅ Media","Se calcula por estación"),
            ("Programación de producción","✅ Media","Asignación de partes a períodos"),
            ("Optimización heurística","✅ Alta","Heurística constructiva"),
            ("Investigación de Operaciones","✅ Media","Modelo matemático de fondo"),
            ("Eficiencia del sistema","✅ Media","Medida a través del desbalance"),
        ]
        st.dataframe(pd.DataFrame(temas, columns=["Tema","Relevancia","Descripción"]),
                     hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 2 — CONFIGURAR FMS
# ══════════════════════════════════════════════════════════════

def modulo_configurar():
    st.markdown('<div class="section-title">⚙️ Configuración del Sistema FMS</div>', unsafe_allow_html=True)

    if st.button("📂 Cargar datos de ejemplo (Medina et al., 2009)", type="primary"):
        st.session_state["cfg"] = datos_ejemplo()
        st.success("✅ Datos de ejemplo cargados.")

    st.markdown("---")
    st.markdown("### 1. Parámetros generales")
    c1, c2, c3, c4 = st.columns(4)
    with c1: n_maq = st.number_input("N° de máquinas", 2, 15, 4)
    with c2: n_par = st.number_input("N° de tipos de partes", 2, 20, 6)
    with c3: n_herr = st.number_input("N° de herramientas", 2, 30, 8)
    with c4: cap = st.number_input("Capacidad portaherramientas (slots)", 2, 50, 6)

    cfg = st.session_state.get("cfg") or {}

    st.markdown("---")
    st.markdown("### 2. Nombres")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Máquinas:**")
        nom_maq = [st.text_input(f"Máquina {i+1}", value=f"M{i+1}", key=f"nm_{i}") for i in range(int(n_maq))]
    with c2:
        st.markdown("**Partes:**")
        nom_par = [st.text_input(f"Parte {i+1}", value=f"P{i+1}", key=f"np_{i}") for i in range(int(n_par))]
    with c3:
        st.markdown("**Herramientas:**")
        nom_herr = [st.text_input(f"Herramienta {i+1}", value=f"H{i+1}", key=f"nh_{i}") for i in range(int(n_herr))]

    st.markdown("---")
    st.markdown("### 3. Tiempos de procesamiento")
    st.caption("Ingresa el tiempo de cada parte en cada máquina. Usa 0 si la parte no requiere esa máquina.")
    tiempos_prev = cfg.get("tiempos", [[0.0]*int(n_maq)]*int(n_par))
    tiempos = []
    for i in range(int(n_par)):
        cols = st.columns([2]+[1]*int(n_maq))
        with cols[0]:
            st.markdown(f"<div style='padding:8px 0;font-weight:600;color:#1e3a5f;'>{nom_par[i]}</div>", unsafe_allow_html=True)
        fila = []
        for j in range(int(n_maq)):
            prev = tiempos_prev[i][j] if i < len(tiempos_prev) and j < len(tiempos_prev[i]) else 0.0
            with cols[j+1]:
                fila.append(st.number_input(nom_maq[j], min_value=0.0, value=float(prev), step=0.5, key=f"t_{i}_{j}"))
        tiempos.append(fila)

    st.markdown("---")
    st.markdown("### 4. Requerimientos de herramientas")
    st.caption("Selecciona las herramientas que necesita cada parte.")
    req_prev = cfg.get("req_herramientas", [[] for _ in range(int(n_par))])
    req_herr = []
    for i in range(int(n_par)):
        prev_set = set(req_prev[i]) if i < len(req_prev) else set()
        cols = st.columns([2]+[1]*int(n_herr))
        with cols[0]:
            st.markdown(f"<div style='padding:4px 0;font-weight:600;color:#1e3a5f;'>{nom_par[i]}</div>", unsafe_allow_html=True)
        req_fila = []
        for k in range(int(n_herr)):
            with cols[k+1]:
                if st.checkbox(nom_herr[k], value=(k in prev_set), key=f"r_{i}_{k}"):
                    req_fila.append(k)
        req_herr.append(req_fila)

    st.markdown("---")
    st.markdown("### 5. Slots por herramienta")
    slots_prev = cfg.get("slots_herramientas", [1]*int(n_herr))
    cols_s = st.columns(min(int(n_herr), 8))
    slots_h = []
    for k in range(int(n_herr)):
        with cols_s[k % 8]:
            slots_h.append(st.number_input(nom_herr[k], 1, 10, int(slots_prev[k]) if k < len(slots_prev) else 1, key=f"s_{k}"))

    st.markdown("---")
    if st.button("💾 Guardar configuración del FMS", type="primary"):
        st.session_state["cfg"] = {
            "n_maquinas": int(n_maq), "n_partes": int(n_par),
            "n_herramientas": int(n_herr), "capacidad": int(cap),
            "nombres_maquinas": nom_maq, "nombres_partes": nom_par,
            "nombres_herramientas": nom_herr, "tiempos": tiempos,
            "req_herramientas": req_herr, "slots_herramientas": slots_h,
        }
        st.session_state["lotes"] = None
        st.success("✅ Configuración guardada. Ve a 'Ejecutar Heurística'.")

    if st.session_state.get("cfg"):
        cfg = st.session_state["cfg"]
        st.markdown("---")
        st.markdown("### Vista previa")
        c1,c2,c3,c4 = st.columns(4)
        for col,lbl,val in [(c1,"Máquinas",cfg['n_maquinas']),(c2,"Partes",cfg['n_partes']),
                            (c3,"Herramientas",cfg['n_herramientas']),(c4,"Capacidad (slots)",cfg['capacidad'])]:
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)
        df_t = pd.DataFrame(cfg["tiempos"], index=cfg["nombres_partes"], columns=cfg["nombres_maquinas"])
        st.markdown("#### Matriz de tiempos")
        st.dataframe(df_t, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 3 — EJECUTAR HEURÍSTICA
# ══════════════════════════════════════════════════════════════

def modulo_ejecutar():
    st.markdown('<div class="section-title">▶ Ejecutar Heurística de Selección de Partes</div>', unsafe_allow_html=True)

    if "cfg" not in st.session_state or not st.session_state["cfg"]:
        st.markdown('<div class="alert-warn">⚠️ Primero configura el FMS en el módulo anterior.</div>', unsafe_allow_html=True)
        return

    cfg = st.session_state["cfg"]
    c1,c2,c3,c4 = st.columns(4)
    for col,lbl,val in [(c1,"Máquinas",cfg['n_maquinas']),(c2,"Partes",cfg['n_partes']),
                        (c3,"Herramientas",cfg['n_herramientas']),(c4,"Cap. portaherramientas",cfg['capacidad'])]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Verificación de factibilidad")
    errores = []
    for i, p in enumerate(cfg["nombres_partes"]):
        s = sum(cfg["slots_herramientas"][k] for k in cfg["req_herramientas"][i])
        if s > cfg["capacidad"]:
            errores.append(f"Parte {p} requiere {s} slots — excede la capacidad de {cfg['capacidad']}")
    if errores:
        for e in errores:
            st.markdown(f'<div class="alert-error">🚨 {e}</div>', unsafe_allow_html=True)
        return
    st.markdown('<div class="alert-ok">✅ Todos los requerimientos son factibles con la capacidad configurada.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="alert-info">ℹ️ La heurística seleccionará en cada paso la parte que genere el <b>menor desbalance de carga</b> entre las estaciones, respetando la restricción de capacidad del portaherramientas (Medina et al., 2009).</div>', unsafe_allow_html=True)

    if st.button("▶ Ejecutar Heurística de Selección de Partes", type="primary", use_container_width=True):
        with st.spinner("Ejecutando heurística..."):
            lotes = heuristica_fms(
                cfg["n_maquinas"], cfg["n_partes"], cfg["capacidad"],
                cfg["tiempos"], cfg["req_herramientas"], cfg["slots_herramientas"],
                cfg["nombres_partes"], cfg["nombres_maquinas"], cfg["nombres_herramientas"]
            )
        st.session_state["lotes"] = lotes
        st.success(f"✅ Heurística ejecutada. Se formaron {len(lotes)} lote(s). Ve a 'Resultados y Análisis'.")
        st.rerun()

    if st.session_state.get("lotes"):
        lotes = st.session_state["lotes"]
        st.markdown("---")
        st.markdown("### Traza de ejecución paso a paso")
        for lote in lotes:
            with st.expander(f"📦 Lote {lote['numero']} — Partes: {', '.join(lote['nombres_partes'])} — ⏱ {lote['tiempo_lote']:.2f}"):
                df_log = pd.DataFrame(lote["log"])
                if not df_log.empty:
                    st.dataframe(df_log, hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 4 — RESULTADOS
# ══════════════════════════════════════════════════════════════

def modulo_resultados():
    st.markdown('<div class="section-title">📈 Resultados y Análisis del FMS</div>', unsafe_allow_html=True)

    if not st.session_state.get("lotes"):
        st.markdown('<div class="alert-warn">⚠️ Primero ejecuta la heurística.</div>', unsafe_allow_html=True)
        return

    lotes = st.session_state["lotes"]
    cfg   = st.session_state["cfg"]
    nom_maq = cfg["nombres_maquinas"]

    tiempo_total = sum(l["tiempo_lote"] for l in lotes)
    n_lotes = len(lotes)
    cuello_g = max(lotes, key=lambda l: l["tiempo_lote"])
    desb_prom = np.mean([l["desbalance"] for l in lotes])

    st.markdown("### KPIs Globales del Sistema")
    c1,c2,c3,c4,c5 = st.columns(5)
    for col,lbl,val,cls in [
        (c1,"Lotes formados",str(n_lotes),""),
        (c2,"Tiempo total",f"{tiempo_total:.2f}","warn"),
        (c3,"Tiempo prom/lote",f"{tiempo_total/n_lotes:.2f}",""),
        (c4,"Cuello global",cuello_g["cuello_botella"],"bad"),
        (c5,"Desbalance prom",f"{desb_prom:.2f}","warn"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value {cls}">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Resumen de lotes formados")
    resumen = [{
        "Lote": f"Lote {l['numero']}",
        "Partes": ", ".join(l["nombres_partes"]),
        "Herramientas": ", ".join(l["nombres_herramientas"]),
        "Slots usados": l["slots_usados"],
        "Cuello de botella": l["cuello_botella"],
        "Tiempo lote": round(l["tiempo_lote"], 3),
        "Desbalance": round(l["desbalance"], 3),
    } for l in lotes]
    st.dataframe(pd.DataFrame(resumen), hide_index=True, use_container_width=True)

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Análisis comparativo")
    st.image(grafica_resumen(lotes, nom_maq), use_column_width=True)

    st.markdown("### Mapa de calor — Carga por máquina y lote")
    st.image(grafica_calor(lotes, nom_maq), use_column_width=True)

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Análisis detallado por lote")
    for lote in lotes:
        with st.expander(f"📦 Lote {lote['numero']} — {', '.join(lote['nombres_partes'])} — ⏱ {lote['tiempo_lote']:.2f}", expanded=True):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"""
                <div class="lote-card">
                <div class="lote-header">📦 Información del Lote {lote['numero']}</div>
                <b>Partes:</b> {", ".join(lote['nombres_partes'])}<br>
                <b>Herramientas:</b> {", ".join(lote['nombres_herramientas'])}<br>
                <b>Slots usados:</b> {lote['slots_usados']} / {cfg['capacidad']}<br>
                <b>Tiempo del lote:</b> {lote['tiempo_lote']:.3f}<br>
                <b>Desbalance:</b> {lote['desbalance']:.3f}<br><br>
                <span class="cuello-badge">🔴 Cuello de botella: {lote['cuello_botella']} 
                (Carga: {lote['cargas'][lote['cuello_idx']]:.3f})</span>
                </div>
                """, unsafe_allow_html=True)
                df_c = pd.DataFrame({
                    "Máquina": nom_maq,
                    "Carga": [round(c, 3) for c in lote["cargas"]],
                    "Utilización (%)": [round(u, 1) for u in lote["utilizacion"]],
                    "¿Cuello?": ["🔴 SÍ" if i == lote["cuello_idx"] else "🟢 No" for i in range(len(nom_maq))],
                })
                st.dataframe(df_c, hide_index=True, use_container_width=True)
            with c2:
                st.image(grafica_cargas(lote, nom_maq), use_column_width=True)
            st.image(grafica_utilizacion(lote, nom_maq), use_column_width=True)

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 💡 Recomendaciones del sistema")
    lote_max_desb = max(lotes, key=lambda l: l["desbalance"])
    recs = [
        f"🔴 El **Lote {cuello_g['numero']}** tiene el mayor tiempo ({cuello_g['tiempo_lote']:.2f}). Priorizar reducción de carga en **{cuello_g['cuello_botella']}** para mejorar el tiempo total.",
        f"⚠️ El **Lote {lote_max_desb['numero']}** tiene el mayor desbalance ({lote_max_desb['desbalance']:.2f}). Redistribuir operaciones entre estaciones.",
        f"📊 Tiempo total de producción: **{tiempo_total:.2f}** unidades para {cfg['n_partes']} tipos de partes en {n_lotes} lote(s).",
        f"🔧 La capacidad del portaherramientas ({cfg['capacidad']} slots) limitó la formación de lotes. Aumentarla podría reducir el número de lotes.",
    ]
    for r in recs:
        st.markdown(f'<div class="alert-info">{r}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 5 — REPORTES
# ══════════════════════════════════════════════════════════════

def modulo_reportes():
    st.markdown('<div class="section-title">📋 Reportes y Exportación</div>', unsafe_allow_html=True)

    if not st.session_state.get("lotes"):
        st.markdown('<div class="alert-warn">⚠️ Primero ejecuta la heurística para generar reportes.</div>', unsafe_allow_html=True)
        return

    lotes = st.session_state["lotes"]
    cfg   = st.session_state["cfg"]
    ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M")

    tab1, tab2, tab3 = st.tabs(["📦 Resumen de Lotes","📊 Cargas por Máquina","🔧 Asignación de Herramientas"])

    with tab1:
        rows = [{"Lote":l["numero"],"Partes":", ".join(l["nombres_partes"]),"N_Partes":len(l["partes"]),
                 "Herramientas":", ".join(l["nombres_herramientas"]),"Slots_Usados":l["slots_usados"],
                 "Capacidad":cfg["capacidad"],"Cuello_Botella":l["cuello_botella"],
                 "Tiempo_Lote":round(l["tiempo_lote"],4),"Desbalance":round(l["desbalance"],4)} for l in lotes]
        df1 = pd.DataFrame(rows)
        st.dataframe(df1, hide_index=True, use_container_width=True)
        st.download_button("⬇️ Descargar resumen de lotes (.csv)",
                           df1.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),
                           f"fms_lotes_{ts}.csv","text/csv",type="primary")

    with tab2:
        rows2 = [{"Lote":l["numero"],"Maquina":m,"Carga":round(l["cargas"][mi],4),
                  "Utilizacion_%":round(l["utilizacion"][mi],2),
                  "Es_Cuello":"SÍ" if mi==l["cuello_idx"] else "No",
                  "Tiempo_Lote":round(l["tiempo_lote"],4)}
                 for l in lotes for mi,m in enumerate(cfg["nombres_maquinas"])]
        df2 = pd.DataFrame(rows2)
        st.dataframe(df2, hide_index=True, use_container_width=True)
        st.download_button("⬇️ Descargar cargas por máquina (.csv)",
                           df2.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),
                           f"fms_cargas_{ts}.csv","text/csv",type="primary")

    with tab3:
        rows3 = [{"Lote":l["numero"],"Parte":cfg["nombres_partes"][p],
                  "Herramienta":cfg["nombres_herramientas"][h],"Slots":cfg["slots_herramientas"][h]}
                 for l in lotes for p in l["partes"] for h in cfg["req_herramientas"][p]]
        df3 = pd.DataFrame(rows3)
        st.dataframe(df3, hide_index=True, use_container_width=True)
        st.download_button("⬇️ Descargar asignación herramientas (.csv)",
                           df3.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),
                           f"fms_herramientas_{ts}.csv","text/csv",type="primary")

    st.markdown("---")
    st.markdown("### Guardar / Cargar configuración")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Exportar configuración actual:**")
        cfg_json = json.dumps(st.session_state["cfg"], indent=2, ensure_ascii=False)
        st.download_button("⬇️ Descargar configuración FMS (.json)",
                           cfg_json.encode("utf-8"), f"fms_config_{ts}.json","application/json")
    with c2:
        st.markdown("**Cargar configuración guardada:**")
        up = st.file_uploader("Subir archivo .json", type=["json"])
        if up:
            try:
                st.session_state["cfg"] = json.load(up)
                st.session_state["lotes"] = None
                st.success("✅ Configuración cargada. Ve a 'Ejecutar Heurística'.")
            except Exception as e:
                st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════
#  MÓDULO 6 — REFERENCIAS APA
# ══════════════════════════════════════════════════════════════

def modulo_referencias():
    st.markdown('<div class="section-title">📚 Referencias Bibliográficas</div>', unsafe_allow_html=True)
    st.markdown("Todas las referencias están en formato **APA 7.ª edición**.")
    st.markdown("---")

    st.markdown("### 📄 Artículo base de la aplicación")
    st.markdown("""
    <div class="ref-card" style="border-left:4px solid #dc2626;">
    Medina Varela, P. D., Cruz Trejos, E. A., & Restrepo Correa, J. H. (2009).
    Problema de formación de lotes de fabricación en un sistema de manufactura flexible:
    Heurística de selección de partes.
    <i>El Hombre y la Máquina, 32</i>, 68–79.
    Universidad Tecnológica de Pereira, Pereira, Colombia.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📖 Libros y manuales de referencia")
    libros = [
        "Groover, M. P. (2007). <i>Automation, production systems, and computer-integrated manufacturing</i> (3.ª ed.). Pearson Prentice Hall.",
        "Chase, R. B., Aquilano, N. J., & Jacobs, F. R. (2005). <i>Administración de producción y operaciones: manufactura y servicios</i> (10.ª ed.). McGraw-Hill.",
        "Sipper, D., & Bulfin, R. L. (1998). <i>Planeación y control de la producción</i>. McGraw-Hill.",
        "Goldratt, E. M., & Cox, J. (1984). <i>The goal: A process of ongoing improvement</i>. North River Press.",
        "Hillier, F. S., & Lieberman, G. J. (2021). <i>Introduction to operations research</i> (11.ª ed.). McGraw-Hill.",
        "Askin, R. G., & Standridge, C. R. (1993). <i>Modeling and analysis of manufacturing systems</i>. John Wiley & Sons.",
    ]
    for r in libros:
        st.markdown(f'<div class="ref-card">{r}</div>', unsafe_allow_html=True)

    st.markdown("### 📰 Artículos científicos relacionados")
    articulos = [
        "Stecke, K. E. (1983). Formulation and solution of nonlinear integer production planning problems for flexible manufacturing systems. <i>Management Science, 29</i>(3), 273–288. https://doi.org/10.1287/mnsc.29.3.273",
        "Kiran, A. S., & Tansel, B. C. (1991). Scheduling in flexible manufacturing systems: A review. <i>International Journal of Production Research, 29</i>(7), 1469–1495. https://doi.org/10.1080/00207549108948020",
        "Kusiak, A. (1985). Flexible manufacturing systems: A structural approach. <i>International Journal of Production Research, 23</i>(6), 1057–1073. https://doi.org/10.1080/00207548508904768",
        "Raj, T., Shankar, R., & Suhaib, M. (2008). An ISM approach for modelling the enablers of flexible manufacturing system: The case for India. <i>International Journal of Production Research, 46</i>(24), 6883–6912.",
    ]
    for r in articulos:
        st.markdown(f'<div class="ref-card">{r}</div>', unsafe_allow_html=True)

    st.markdown("### 🌐 Recursos digitales")
    web = [
        "Aquilano, N. J., Chase, R. B., & Davis, M. M. (2000). <i>Fundamentos de dirección y administración de empresas</i>. Irwin/McGraw-Hill.",
        "Universidad Tecnológica de Pereira. (2024). <i>FMS.lab: Herramienta didáctica para formación de lotes en sistemas de manufactura flexible</i> [Software]. Desarrollado con Python y Streamlit. Producción III — Ingeniería Industrial.",
    ]
    for r in web:
        st.markdown(f'<div class="ref-card">{r}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    if "cfg"   not in st.session_state: st.session_state["cfg"]   = None
    if "lotes" not in st.session_state: st.session_state["lotes"] = None

    mostrar_header()
    mod = sidebar_nav()

    if   "Marco"      in mod: modulo_teoria()
    elif "Configurar" in mod: modulo_configurar()
    elif "Ejecutar"   in mod: modulo_ejecutar()
    elif "Resultados" in mod: modulo_resultados()
    elif "Reportes"   in mod: modulo_reportes()
    elif "Referencias" in mod: modulo_referencias()

if __name__ == "__main__":
    main()
