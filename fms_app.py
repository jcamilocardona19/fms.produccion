"""
FMS.lab — Formación de Lotes en Sistemas de Manufactura Flexible
Universidad Tecnológica de Pereira — Producción III

Implementación de la heurística de selección de partes de:
Medina Varela, P. D., Cruz Trejos, E. A. & Restrepo Correa, J. H. (2009).
Problema de formación de lotes de fabricación en un sistema de manufactura
flexible: Heurística de selección de partes. El Hombre y la Máquina, 32, 68-79.
"""

from dataclasses import dataclass, field
import io, json, datetime, copy

import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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

[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#0f2440 0%,#1a3a5c 60%,#0d1e35 100%);
    border-right:1px solid #1e3a5f;
}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
[data-testid="stSidebar"] .stRadio label{color:#e2e8f0!important;padding:6px 0;}

.metric-card{
    background:white;border:1px solid #e2e8f0;border-radius:12px;
    padding:18px 20px;text-align:center;
    box-shadow:0 2px 8px rgba(0,0,0,0.07);margin-bottom:8px;transition:transform 0.2s;
}
.metric-card:hover{transform:translateY(-2px);}
.metric-label{font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;color:#64748b;font-weight:600;margin-bottom:6px;}
.metric-value{font-size:1.4rem;font-weight:700;color:#1e3a5f;font-family:'IBM Plex Mono',monospace;}
.metric-value.ok{color:#16a34a;}
.metric-value.bad{color:#dc2626;}
.metric-value.warn{color:#d97706;}

.alert-ok{background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:12px 16px;color:#166534;margin:8px 0;}
.alert-warn{background:#fffbeb;border:1px solid #fcd34d;border-radius:10px;padding:12px 16px;color:#92400e;margin:8px 0;}
.alert-error{background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:12px 16px;color:#991b1b;margin:8px 0;}
.alert-info{background:#eff6ff;border:1px solid #93c5fd;border-radius:10px;padding:12px 16px;color:#1e40af;margin:8px 0;}

.section-title{
    font-size:1.4rem;font-weight:700;color:#1e3a5f;
    border-bottom:3px solid #2563eb;padding-bottom:10px;margin-bottom:24px;letter-spacing:-0.3px;
}

.teoria-card{
    background:white;border:1px solid #e2e8f0;border-radius:12px;padding:20px;
    margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,0.05);line-height:1.7;
}
.teoria-card h4{color:#1e3a5f;margin-bottom:10px;font-size:1rem;border-left:3px solid #2563eb;padding-left:8px;}

.lote-card{
    background:white;border:1px solid #e2e8f0;border-radius:12px;padding:20px;
    margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,0.06);
}
.lote-header{font-size:1.05rem;font-weight:700;color:#1e3a5f;margin-bottom:10px;}

.decision-ok{
    background:#f0fdf4;border:1px solid #86efac;border-radius:8px;
    padding:8px 14px;font-size:0.88rem;color:#166534;margin:6px 0;display:inline-block;
}
.decision-frac{
    background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;
    padding:8px 14px;font-size:0.88rem;color:#92400e;margin:6px 0;display:inline-block;
}
.decision-no{
    background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;
    padding:8px 14px;font-size:0.88rem;color:#991b1b;margin:6px 0;display:inline-block;
}

.formula-box{
    background:#f1f5f9;border-left:4px solid #2563eb;border-radius:0 10px 10px 0;
    padding:14px 18px;font-family:'IBM Plex Mono',monospace;font-size:0.88rem;
    color:#1e3a5f;margin:12px 0;line-height:2;white-space:pre-wrap;
}

.ref-card{
    background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 18px;
    margin-bottom:10px;font-size:0.88rem;color:#374151;line-height:1.8;border-left:3px solid #2563eb;
}

.stButton>button{
    background:linear-gradient(135deg,#2563eb,#1d4ed8);color:white;border:none;
    border-radius:10px;font-weight:600;font-size:0.95rem;padding:10px 24px;
    box-shadow:0 2px 8px rgba(37,99,235,0.3);transition:all 0.2s;
}
.stButton>button:hover{
    background:linear-gradient(135deg,#1d4ed8,#1e40af);
    box-shadow:0 4px 12px rgba(37,99,235,0.4);transform:translateY(-1px);
}

.banner-utp{
    background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 60%,#1e40af 100%);
    border-radius:14px;padding:28px 32px;margin-bottom:28px;color:white;
    box-shadow:0 4px 20px rgba(37,99,235,0.25);
}
.banner-title{font-size:1.7rem;font-weight:700;letter-spacing:-0.5px;margin-bottom:4px;}
.banner-sub{font-size:0.9rem;color:#bfdbfe;line-height:1.6;}

.grad-divider{
    height:3px;background:linear-gradient(90deg,#2563eb,#7c3aed,#2563eb);
    border:none;border-radius:2px;margin:24px 0;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  NÚCLEO — MODELO DE DATOS
#  (Python puro: no importa Streamlit ni Matplotlib)
# ══════════════════════════════════════════════════════════════

EPS = 1e-9


class InfactibilidadError(Exception):
    pass


@dataclass
class MachineType:
    """Un tipo de máquina del FMS."""
    code: str
    n_machines: int          # m_j
    hours_per_machine: float # P_j
    holders_per_machine: int # K_j

    @property
    def cap_tiempo(self):
        """Tiempo disponible por lote: m_j x P_j"""
        return self.n_machines * self.hours_per_machine

    @property
    def cap_herr(self):
        """Espacios de herramienta por lote: m_j x K_j"""
        return self.n_machines * self.holders_per_machine


@dataclass
class Order:
    """Un pedido (no un tipo de parte: la misma parte puede tener varios pedidos)."""
    oid: int
    part: str                # tipo de parte
    size: int                # u_i
    due: float               # d_i
    unit_time: dict          # p_ij por código de tipo de máquina
    tools: dict              # herramientas por código de tipo de máquina
    orden_captura: int = 0
    pendiente: int = None

    def __post_init__(self):
        if self.pendiente is None:
            self.pendiente = self.size

    def usa(self, j):
        """Regla clave: si p_ij = 0 la pieza no usa esa máquina."""
        return self.unit_time.get(j, 0.0) > 0

    def tiempo_total(self):
        """u_i x suma de p_ij sobre todos los tipos de máquina. Rompe empates."""
        return self.size * sum(self.unit_time.values())


@dataclass
class Lot:
    """Estado de un lote en formación."""
    indice: int
    used_time: dict = field(default_factory=dict)   # T_j
    tools: dict = field(default_factory=dict)       # herramientas en orden de carga
    motivo_cierre: list = field(default_factory=list)


# ══════════════════════════════════════════════════════════════
#  NÚCLEO — ALGORITMO
# ══════════════════════════════════════════════════════════════

def paso1_ordenar(pedidos):
    """PASO 1: fecha de entrega ascendente; empates por mayor tiempo total;
    segundo empate por orden de digitación (determinismo)."""
    return sorted(pedidos, key=lambda p: (p.due, -p.tiempo_total(), p.orden_captura))


def herramientas_nuevas(lote, pedido, j):
    """Solo cuentan las herramientas que aún no están cargadas en el lote."""
    return [h for h in pedido.tools.get(j, ()) if h not in lote.tools[j]]


def diagnostico_herramientas(lote, pedido, tipos):
    """Devuelve None si caben; si no, el tipo de máquina que bloquea."""
    for j, mt in tipos.items():
        if not pedido.usa(j):
            continue
        nuevas = herramientas_nuevas(lote, pedido, j)
        if len(lote.tools[j]) + len(nuevas) > mt.cap_herr:
            return {
                "tipo": j,
                "cargadas": len(lote.tools[j]),
                "nuevas": nuevas,
                "capacidad": mt.cap_herr,
            }
    return None


def cantidad_maxima(lote, pedido, tipos):
    """Cuántas unidades del pedido caben en el lote actual.
    Devuelve (q, detalle) donde detalle explica la decisión."""
    detalle = {"herramientas": {}, "tiempo": {}, "bloqueo_herr": None, "restriccion": None}

    bloqueo = diagnostico_herramientas(lote, pedido, tipos)
    if bloqueo is not None:
        detalle["bloqueo_herr"] = bloqueo
        detalle["restriccion"] = f"herramientas en {bloqueo['tipo']}"
        return 0, detalle

    for j, mt in tipos.items():
        if not pedido.usa(j):
            detalle["herramientas"][j] = None   # máquina ignorada
            continue
        detalle["herramientas"][j] = {
            "cargadas": list(lote.tools[j]),
            "nuevas": herramientas_nuevas(lote, pedido, j),
            "capacidad": mt.cap_herr,
        }

    q = pedido.pendiente
    detalle["restriccion"] = "unidades pendientes del pedido"
    for j, mt in tipos.items():
        p = pedido.unit_time.get(j, 0.0)
        if p <= 0:
            continue
        libre = mt.cap_tiempo - lote.used_time[j]
        caben = int((libre + EPS) // p)
        detalle["tiempo"][j] = {"libre": round(libre, 6), "unitario": p, "caben": caben}
        if caben < q:
            q = caben
            detalle["restriccion"] = f"tiempo disponible en {j}"

    return max(q, 0), detalle


def asignar(lote, pedido, q, tipos):
    """Descuenta recursos y carga herramientas conservando el ORDEN de carga."""
    consumo = {}
    for j in tipos:
        p = pedido.unit_time.get(j, 0.0)
        if p <= 0:
            consumo[j] = 0.0
            continue
        consumo[j] = round(q * p, 6)
        lote.used_time[j] = round(lote.used_time[j] + q * p, 6)
        for h in pedido.tools.get(j, ()):
            if h not in lote.tools[j]:
                lote.tools[j].append(h)
    pedido.pendiente -= q
    return consumo


def ejecutar(pedidos, tipos):
    """PASO 2: recorre la fila del Paso 1 metiendo pedidos al lote abierto.
    Una sola pasada por lote (las capacidades solo disminuyen)."""
    pendientes = paso1_ordenar(copy.deepcopy(pedidos))
    lotes, bitacora, k = [], [], 0

    while any(p.pendiente > 0 for p in pendientes):
        lote = Lot(
            indice=len(lotes) + 1,
            used_time={j: 0.0 for j in tipos},
            tools={j: [] for j in tipos},
        )
        lotes.append(lote)
        hubo_avance = False

        for pedido in pendientes:
            if pedido.pendiente == 0:
                continue

            pendiente_antes = pedido.pendiente
            q, detalle = cantidad_maxima(lote, pedido, tipos)

            if q == 0:
                lote.motivo_cierre.append({
                    "parte": pedido.part, "oid": pedido.oid,
                    "pendientes": pendiente_antes, "detalle": detalle,
                })
                continue

            consumo = asignar(lote, pedido, q, tipos)
            hubo_avance = True
            k += 1
            bitacora.append({
                "iteracion": k,
                "lote": lote.indice,
                "parte": pedido.part,
                "oid": pedido.oid,
                "asignadas": q,
                "tam_original": pedido.size,
                "pendiente_antes": pendiente_antes,
                "resto": pedido.pendiente,
                "fraccionado": pedido.pendiente > 0,
                "consumo": consumo,
                "t_acum": dict(lote.used_time),
                "herr_acum": {j: list(v) for j, v in lote.tools.items()},
                "detalle": detalle,
            })

        if not hubo_avance:
            raise InfactibilidadError(
                "Se abrió un lote vacío y ningún pedido pendiente pudo entrar. "
                "Revisa las capacidades del sistema."
            )

    return lotes, bitacora


def validar(tipos, pedidos):
    """Reglas de infactibilidad y advertencias antes de ejecutar."""
    errores, avisos = [], []

    codigos = [mt.code for mt in tipos.values()]
    if len(codigos) != len(set(codigos)):
        errores.append("Hay códigos de tipo de máquina repetidos.")

    for mt in tipos.values():
        if mt.cap_tiempo <= 0:
            errores.append(f"El tipo {mt.code} no tiene tiempo disponible (m x P = 0).")
        if mt.cap_herr <= 0:
            errores.append(f"El tipo {mt.code} no tiene portaherramientas disponibles.")

    for p in pedidos:
        if p.size <= 0:
            errores.append(f"El pedido {p.oid} ({p.part}) tiene tamaño de orden inválido.")
        if sum(p.unit_time.values()) <= 0:
            avisos.append(f"El pedido {p.oid} ({p.part}) no consume tiempo en ninguna máquina.")
        for j, mt in tipos.items():
            if not p.usa(j):
                continue
            n_h = len(set(p.tools.get(j, [])))
            if n_h > mt.cap_herr:
                errores.append(
                    f"El pedido {p.oid} ({p.part}) exige {n_h} herramientas en {j}, "
                    f"pero solo hay {mt.cap_herr} espacios. Nunca cabría ni en un lote vacío."
                )
            if p.unit_time[j] > mt.cap_tiempo + EPS:
                errores.append(
                    f"Una sola unidad del pedido {p.oid} ({p.part}) necesita "
                    f"{p.unit_time[j]} h en {j}, más que las {mt.cap_tiempo} h del lote."
                )
    return errores, avisos


# ══════════════════════════════════════════════════════════════
#  NÚCLEO — TABLAS
# ══════════════════════════════════════════════════════════════

def num(x, dec=2):
    """Formato con coma decimal, como el artículo."""
    s = f"{x:.{dec}f}".rstrip("0").rstrip(".")
    if s in ("", "-"):
        s = "0"
    return s.replace(".", ",")


def tabla2(pedidos, tipos):
    """Resultado del Paso 1: la fila de espera ordenada."""
    filas = []
    for i, p in enumerate(paso1_ordenar(pedidos), 1):
        fila = {
            "Orden": i,
            "Tipo de parte": p.part,
            "Tamaño de la orden": p.size,
            "Fecha de entrega": p.due,
        }
        for j in tipos:
            fila[f"Máq. {j} (h/und)"] = p.unit_time.get(j, 0.0)
        fila["Herramientas"] = ", ".join(
            h for j in tipos if p.usa(j) for h in p.tools.get(j, [])
        )
        fila["Tiempo total (h)"] = round(p.tiempo_total(), 4)
        filas.append(fila)
    return pd.DataFrame(filas)


def tabla3(bitacora, tipos, formato=True):
    """Resumen de iteraciones: acumulados dentro del lote tras cada asignación."""
    filas = []
    for r in bitacora:
        etiqueta = f"{r['parte']} ({r['asignadas']}/{r['tam_original']})"
        fila = {"Iteración": r["iteracion"], "Parte asignada": etiqueta, "Lote": r["lote"]}
        for j in tipos:
            v = r["t_acum"][j]
            fila[f"Tiempo acum. {j}"] = num(v) if formato else round(v, 4)
        for j in tipos:
            fila[f"Herramientas acum. {j}"] = ", ".join(r["herr_acum"][j])
        filas.append(fila)
    return pd.DataFrame(filas)


def tabla4(lotes, tipos, formato=True):
    """% de utilización = tiempo acumulado del lote / (m_j x P_j) x 100."""
    filas = []
    for l in lotes:
        fila = {"Lote": l.indice}
        for j, mt in tipos.items():
            u = l.used_time[j] / mt.cap_tiempo * 100 if mt.cap_tiempo else 0
            fila[f"% utilización Máquina {j}"] = f"{num(u)} %" if formato else round(u, 2)
        filas.append(fila)
    return pd.DataFrame(filas)


# ══════════════════════════════════════════════════════════════
#  GRÁFICAS — LÍNEAS DE TIEMPO Y DE PORTAHERRAMIENTAS
# ══════════════════════════════════════════════════════════════

PALETA = ["#2563eb", "#7c3aed", "#0891b2", "#16a34a", "#d97706", "#db2777", "#4f46e5", "#0d9488"]
GRIS_BORDE = "#cbd5e1"


def lineas_estado(bitacora, iteracion, tipos):
    """Líneas de tiempo y de portaherramientas del lote, tal como la Figura del artículo.
    Muestra la foto del lote justo después de la iteración indicada."""
    fila = next(r for r in bitacora if r["iteracion"] == iteracion)
    lote_id = fila["lote"]
    previas = [r for r in bitacora if r["lote"] == lote_id and r["iteracion"] <= iteracion]

    n = len(tipos)
    fig, axes = plt.subplots(2 * n, 1, figsize=(11, 1.15 * 2 * n + 0.6), facecolor="white")
    if 2 * n == 1:
        axes = [axes]
    fig.suptitle(f"Lote {lote_id} — estado tras la iteración {iteracion}",
                 fontweight="bold", color="#1e3a5f", fontsize=12, y=0.99)

    for idx, (j, mt) in enumerate(tipos.items()):
        # ---- Barra de tiempo ----
        ax = axes[2 * idx]
        cursor = 0.0
        for k, r in enumerate(previas):
            w = r["consumo"].get(j, 0.0)
            if w <= 0:
                continue
            color = PALETA[(r["iteracion"] - 1) % len(PALETA)]
            destaca = r["iteracion"] == iteracion
            ax.broken_barh([(cursor, w)], (0.15, 0.7), facecolors=color,
                           edgecolor="white" if not destaca else "#0f172a",
                           linewidth=1.6 if destaca else 0.8, zorder=3)
            if w / mt.cap_tiempo > 0.06:
                ax.text(cursor + w / 2, 0.5, r["parte"], ha="center", va="center",
                        color="white", fontsize=8.5, fontweight="bold", zorder=4)
            cursor += w
        libre = mt.cap_tiempo - cursor
        if libre > EPS:
            ax.broken_barh([(cursor, libre)], (0.15, 0.7), facecolors="white",
                           edgecolor=GRIS_BORDE, linewidth=1.0, zorder=2)
        ax.set_xlim(0, mt.cap_tiempo)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_ylabel(f"Tiempo {j}", rotation=0, ha="right", va="center",
                      fontsize=9.5, color="#1e3a5f", fontweight="bold", labelpad=12)
        ax.set_xticks([0, mt.cap_tiempo])
        ax.set_xticklabels(["0", f"{num(mt.cap_tiempo)} h"], fontsize=8.5, color="#64748b")
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(length=0)
        ax.text(mt.cap_tiempo * 1.012, 0.5,
                f"{num(cursor)} / {num(mt.cap_tiempo)} h",
                va="center", fontsize=9, fontfamily="monospace", color="#1e3a5f")

        # ---- Barra de portaherramientas ----
        ax2 = axes[2 * idx + 1]
        cargadas = fila["herr_acum"][j]
        for c in range(mt.cap_herr):
            ocupada = c < len(cargadas)
            ax2.broken_barh([(c + 0.04, 0.92)], (0.2, 0.6),
                            facecolors="#dbeafe" if ocupada else "white",
                            edgecolor="#2563eb" if ocupada else GRIS_BORDE,
                            linewidth=1.2, zorder=3)
            if ocupada:
                ax2.text(c + 0.5, 0.5, cargadas[c], ha="center", va="center",
                         fontsize=8.5, fontweight="bold", color="#1e3a5f", zorder=4)
        ax2.set_xlim(0, mt.cap_herr)
        ax2.set_ylim(0, 1)
        ax2.set_yticks([])
        ax2.set_xticks([])
        ax2.set_ylabel(f"Portaherr. {j}", rotation=0, ha="right", va="center",
                       fontsize=9.5, color="#1e3a5f", fontweight="bold", labelpad=12)
        for sp in ax2.spines.values():
            sp.set_visible(False)
        ax2.text(mt.cap_herr * 1.012, 0.5, f"{len(cargadas)} / {mt.cap_herr}",
                 va="center", fontsize=9, fontfamily="monospace", color="#1e3a5f")

    fig.subplots_adjust(right=0.86, hspace=0.55, top=0.90)
    return fig


def barras_utilizacion(lotes, tipos):
    """Utilización final por lote y tipo de máquina (Tabla 4 en gráfico)."""
    fig, ax = plt.subplots(figsize=(10, 3.6), facecolor="white")
    ancho = 0.8 / max(len(tipos), 1)
    for k, (j, mt) in enumerate(tipos.items()):
        xs = [i + k * ancho for i in range(len(lotes))]
        ys = [l.used_time[j] / mt.cap_tiempo * 100 if mt.cap_tiempo else 0 for l in lotes]
        barras = ax.bar(xs, ys, width=ancho, label=f"Máquina {j}",
                        color=PALETA[k % len(PALETA)], edgecolor="white", linewidth=1.5, zorder=3)
        for b, v in zip(barras, ys):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.2f}%".replace(".", ","),
                    ha="center", va="bottom", fontsize=8.5, fontfamily="monospace", color="#374151")
    ax.set_xticks([i + ancho * (len(tipos) - 1) / 2 for i in range(len(lotes))])
    ax.set_xticklabels([f"Lote {l.indice}" for l in lotes], fontsize=10)
    ax.set_ylabel("% de utilización", color="#1e3a5f", fontsize=10)
    ax.set_ylim(0, 112)
    ax.axhline(100, color=GRIS_BORDE, linestyle="--", linewidth=1.2, zorder=2)
    ax.grid(True, axis="y", color="#e2e8f0", linestyle="--", alpha=0.9, zorder=1)
    ax.set_facecolor("#f8fafc")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=9, framealpha=0.95, facecolor="white", edgecolor="#e2e8f0")
    ax.set_title("Utilización de cada tipo de máquina por lote",
                 fontweight="bold", color="#1e3a5f", fontsize=12, pad=10)
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════
#  CASO DEL ARTÍCULO (Tabla 1)
# ══════════════════════════════════════════════════════════════

def caso_articulo():
    return {
        "tipos": [
            {"code": "A", "m": 3, "P": 12.0, "K": 2},
            {"code": "B", "m": 1, "P": 12.0, "K": 2},
        ],
        "pedidos": [
            {"parte": "a", "size": 5,  "due": 0, "t_A": 0.1, "h_A": "A1", "t_B": 0.3, "h_B": "B2"},
            {"parte": "b", "size": 10, "due": 1, "t_A": 1.2, "h_A": "A2", "t_B": 0.0, "h_B": ""},
            {"parte": "c", "size": 25, "due": 1, "t_A": 0.7, "h_A": "A3", "t_B": 0.4, "h_B": "B4"},
            {"parte": "d", "size": 10, "due": 1, "t_A": 0.1, "h_A": "A1", "t_B": 0.2, "h_B": "B2"},
            {"parte": "e", "size": 4,  "due": 2, "t_A": 0.3, "h_A": "A5", "t_B": 0.2, "h_B": "B3"},
            {"parte": "a", "size": 10, "due": 4, "t_A": 0.3, "h_A": "A1", "t_B": 0.2, "h_B": "B2"},
        ],
    }


def val_num(v, default=0.0):
    """Convierte un valor de st.data_editor a número. Las filas nuevas llegan
    con NaN, y NaN es truthy: sin este filtro, int(NaN or 0) lanza ValueError."""
    try:
        if v is None or pd.isna(v):
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def val_txt(v, default=""):
    """Idem para columnas de texto."""
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return default
    return str(v)


def cfg_a_objetos(cfg):
    """Traduce la configuración de la interfaz a los objetos del núcleo."""
    tipos = {}
    for t in cfg["tipos"]:
        code = str(t["code"]).strip()
        if not code:
            continue
        tipos[code] = MachineType(code, int(val_num(t.get("m"), 1)),
                                  val_num(t.get("P"), 0.0), int(val_num(t.get("K"), 1)))

    pedidos = []
    for i, p in enumerate(cfg["pedidos"]):
        unit, tools = {}, {}
        for j in tipos:
            unit[j] = val_num(p.get(f"t_{j}"), 0.0)
            crudo = val_txt(p.get(f"h_{j}"))
            lista, vistas = [], set()
            for h in crudo.replace(";", ",").split(","):
                h = h.strip()
                if h and h not in vistas:
                    vistas.add(h)
                    lista.append(h)
            tools[j] = lista
        pedidos.append(Order(
            oid=i + 1, part=val_txt(p.get("parte")).strip() or f"P{i+1}",
            size=int(val_num(p.get("size"), 0)), due=val_num(p.get("due"), 0),
            unit_time=unit, tools=tools, orden_captura=i,
        ))
    return tipos, pedidos


# ══════════════════════════════════════════════════════════════
#  INTERFAZ — CABECERA Y NAVEGACIÓN
# ══════════════════════════════════════════════════════════════

def mostrar_header():
    col1, col2 = st.columns([1, 6])
    with col1:
        try:
            st.image("utp_logo.png", width=105)
        except Exception:
            st.markdown("**UTP**")
    with col2:
        st.markdown("""
        <div class="banner-utp">
            <div class="banner-title">🏭 FMS.lab — Formación de Lotes de Fabricación</div>
            <div class="banner-sub">
            Universidad Tecnológica de Pereira &nbsp;·&nbsp; Ingeniería Industrial &nbsp;·&nbsp; Producción III<br>
            Heurística de Selección de Partes en Sistemas de Manufactura Flexible (FMS)<br>
            <span style="opacity:0.8;font-size:0.85rem;">
            Medina Varela, Cruz Trejos &amp; Restrepo Correa (2009)
            </span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def sidebar_nav():
    with st.sidebar:
        try:
            st.image("utp_logo.png", width=130)
        except Exception:
            pass
        st.markdown("---")
        st.markdown("### 🏭 Navegación")
        modulo = st.radio("", [
            "📖 Marco Teórico",
            "⚙️ Configurar FMS",
            "▶ Ejecutar Algoritmo",
            "📈 Resultados y Análisis",
            "📋 Reportes",
            "📚 Referencias",
        ], label_visibility="collapsed")
        st.markdown("---")
        if st.session_state.get("cfg"):
            tipos, _ = cfg_a_objetos(st.session_state["cfg"])
            resumen = " · ".join(
                f"{j}: {num(mt.cap_tiempo)} h / {mt.cap_herr} esp." for j, mt in tipos.items()
            )
            st.markdown(
                f"<div style='font-size:0.76rem;color:#bfdbfe;line-height:1.7;'>"
                f"<b>Capacidad por lote</b><br>{resumen}</div>",
                unsafe_allow_html=True)
            st.markdown("---")
        st.markdown("""
        <div style='font-size:0.76rem;color:#94a3b8;line-height:1.9;'>
        <b style='color:#bfdbfe;'>Referencia principal</b><br>
        Medina, Cruz &amp; Restrepo<br>
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
    st.markdown('<div class="section-title">📖 Marco Teórico — FMS y Formación de Lotes</div>',
                unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["🏭 ¿Qué es un FMS?", "📦 El Problema",
                              "🧮 La Heurística", "🎓 Producción III"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="teoria-card">
            <h4>🏭 Sistema de Manufactura Flexible (FMS)</h4>
            Un FMS es un sistema de producción automatizado con cuatro características:
            <ul>
            <li><b>Estaciones CNC</b> reprogramables automáticamente</li>
            <li><b>Cambio y entrega automática</b> de herramientas</li>
            <li><b>Manejo automático de materiales</b> entre estaciones</li>
            <li><b>Control central</b> del sistema</li>
            </ul>
            Cada máquina puede fabricar cualquier pieza, siempre que tenga cargadas
            las herramientas que esa pieza necesita.
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="teoria-card">
            <h4>⚙️ Portaherramientas — la restricción que obliga a formar lotes</h4>
            Cada máquina tiene un número limitado de portaherramientas. Si las herramientas
            que exigen todos los pedidos <b>no caben al mismo tiempo</b> en el sistema,
            no se puede producir todo de una vez: hay que <b>formar lotes</b> que se
            fabrican secuencialmente, con un alistamiento nuevo entre uno y otro.
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="teoria-card">
            <h4>📦 Lote de fabricación</h4>
            Un lote es una cantidad específica de cada tipo de parte que se fabrica
            en un periodo determinado:
            <ol>
            <li>Se alista el sistema para el lote</li>
            <li>Se cargan <b>todas</b> las herramientas necesarias al inicio</li>
            <li>Se fabrican todas las partes del lote</li>
            <li>Se vuelve a alistar el sistema para el siguiente</li>
            </ol>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="teoria-card">
            <h4>🎯 Los tres objetivos del método</h4>
            <ul>
            <li>Ubicar las piezas en lotes de modo que cada lote use todas las máquinas</li>
            <li>Que cada lote requiera un número limitado de herramientas</li>
            <li>Que las piezas de un lote tengan <b>fechas de entrega similares</b></li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### Los dos contextos identificados en el artículo (Figura 1)")
        st.dataframe(pd.DataFrame({
            "Contexto": ["Portaherramientas < herramientas necesarias",
                         "Portaherramientas = herramientas necesarias"],
            "Acción": ["Formación de lotes", "Iniciar producción directamente"],
            "Este aplicativo": ["✅ Es el caso que resuelve", "❌ No requiere el método"],
        }), hide_index=True, use_container_width=True)

    with t2:
        st.markdown('<div class="alert-info">📌 <b>Pregunta central:</b> ¿qué pedidos '
                    'entran en cada lote, respetando el tiempo disponible de máquina y '
                    'los portaherramientas, y atendiendo primero lo más urgente?</div>',
                    unsafe_allow_html=True)

        st.markdown("#### Los dos recursos que se controlan")
        st.dataframe(pd.DataFrame({
            "Recurso": ["Tiempo del tipo de máquina j", "Portaherramientas del tipo j"],
            "Cuánto hay disponible": ["mⱼ × Pⱼ  (máquinas × horas del turno)",
                                      "mⱼ × Kⱼ  (máquinas × portaherr. por máquina)"],
            "Cómo se consume": ["uᵢ × pᵢⱼ  (unidades × tiempo unitario)",
                                "una herramienta ocupa un solo espacio por lote, "
                                "aunque la usen varios pedidos"],
        }), hide_index=True, use_container_width=True)

        st.markdown("#### Notación del artículo")
        st.dataframe(pd.DataFrame({
            "Símbolo": ["dᵢ", "uᵢ", "pᵢⱼ", "mⱼ", "Pⱼ", "Kⱼ", "Tⱼ", "kⱼ"],
            "Significado": [
                "Fecha de entrega del pedido de la parte i",
                "Número de unidades del pedido de la parte i",
                "Tiempo unitario de producción de la parte i en la máquina tipo j",
                "Número de máquinas tipo j en el sistema",
                "Tiempo disponible por máquina tipo j por periodo (el turno)",
                "Portaherramientas por máquina tipo j",
                "Tiempo ya asignado a máquinas tipo j en el lote actual",
                "Portaherramientas ya ocupados en máquinas tipo j"],
            "De dónde sale": ["Pedido", "Pedido", "Pedido", "Configuración",
                              "Configuración", "Configuración", "Lo calcula el programa",
                              "Lo calcula el programa"],
        }), hide_index=True, use_container_width=True)

        st.markdown("#### Las dos restricciones del modelo")
        st.markdown("""
        <div class="formula-box">Restricción de tiempo:            Tⱼ ≤ mⱼ × Pⱼ
Restricción de portaherramientas:  kⱼ ≤ mⱼ × Kⱼ</div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="alert-warn">⚠️ <b>Regla que decide medio ejemplo:</b> '
                    'si el tiempo unitario de una pieza en una máquina es <b>cero</b>, esa '
                    'pieza no usa esa máquina: no consume ni su tiempo ni sus '
                    'portaherramientas, y esa máquina ni siquiera se revisa.</div>',
                    unsafe_allow_html=True)

    with t3:
        st.markdown("#### Paso 1 — Ordenar los pedidos")
        st.markdown("""
        <div class="teoria-card">
        Se ordenan todos los pedidos por <b>fecha de entrega</b>, de la más cercana a la más
        lejana. Ese orden no se vuelve a tocar: es la fila de espera del método.<br><br>
        <b>Empate en fecha:</b> va primero el pedido que más tiempo total de producción
        genera en el sistema (lo pesado se acomoda primero).<br>
        <b>Empate también en tiempo total:</b> el artículo no lo define; el programa conserva
        el orden en que se digitaron los pedidos para ser determinista.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="formula-box">Tiempo total del pedido i = uᵢ × ( Σⱼ pᵢⱼ )   sobre TODOS los tipos de máquina</div>
        """, unsafe_allow_html=True)

        st.markdown("#### Paso 2 — Meter los pedidos en los lotes")
        st.markdown("""
        <div class="teoria-card">
        Para cada pedido de la fila se hacen <b>dos preguntas, siempre en este orden</b>:<br><br>
        <b>1. ¿Caben las herramientas?</b> Se cuentan solo las <i>nuevas</i>: las que el pedido
        necesita y todavía no están cargadas en el lote. Una herramienta ya cargada es gratis.
        Si falla en algún tipo de máquina, el pedido no entra — ni completo ni fraccionado.<br><br>
        <b>2. ¿Cuántas unidades caben en tiempo?</b> Por cada tipo de máquina se calcula la parte
        entera de (tiempo libre ÷ tiempo unitario). El valor final <b>q</b> es el mínimo entre las
        unidades pendientes y lo que admite cada máquina: manda la más apretada.
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Resultado de q": ["q = todas las unidades pendientes",
                               "0 < q < unidades pendientes", "q = 0"],
            "Significado": ["El pedido cabe completo", "El pedido cabe a medias",
                            "No cabe ni una unidad"],
            "Qué hace el programa": [
                "Se asigna completo y sigue con el siguiente pedido",
                "Se fracciona: q unidades ahora, el resto en el siguiente lote",
                "Se salta y se intenta con el siguiente de la fila (barrido)"],
        }), hide_index=True, use_container_width=True)

        st.markdown('<div class="alert-info">📌 <b>El barrido:</b> si un pedido no cabe, el lote '
                    '<b>no</b> se cierra de inmediato. Se intenta con el siguiente, y con el '
                    'siguiente, hasta el último. Un pedido pequeño puede caber donde el grande no '
                    'cupo. El lote se cierra solo cuando, tras recorrer toda la fila, ningún '
                    'pendiente pudo entrar. Al abrir el lote nuevo todo vuelve a cero: es un '
                    'alistamiento nuevo del sistema.</div>', unsafe_allow_html=True)

        st.markdown("#### Pseudocódigo del motor")
        st.code('''
PASO 1
    pendientes ← ordenar por (fecha ↑, tiempo total ↓, orden de digitación)

PASO 2
    MIENTRAS queden unidades pendientes:
        lote ← nuevo lote (tiempos en cero, portaherramientas vacíos)
        hubo_avance ← Falso

        PARA cada pedido en pendientes:          # una sola pasada = el barrido
            SI pedido.pendiente = 0 → continuar

            # Pregunta 1: herramientas
            PARA cada tipo de máquina j que la pieza SÍ usa (p_ij > 0):
                SI cargadas(j) + nuevas(pedido, j) > m_j × K_j:
                    q ← 0 ; salir

            # Pregunta 2: tiempo
            q ← unidades pendientes del pedido
            PARA cada tipo de máquina j que la pieza SÍ usa:
                libre ← m_j × P_j − T_j
                q ← mínimo( q , parte entera de (libre / p_ij) )

            SI q = 0 → continuar con el siguiente pedido

            asignar q unidades: T_j += q × p_ij ; cargar herramientas nuevas
            pedido.pendiente −= q
            hubo_avance ← Verdadero
            registrar iteración en la bitácora

        SI NO hubo_avance → datos infactibles (protección contra ciclo infinito)

FIN cuando no queden unidades pendientes
        ''', language="text")

        st.markdown('<div class="alert-warn">⚠️ <b>Dos detalles de implementación.</b> '
                    'Basta una sola pasada por lote: dentro de un lote las capacidades solo '
                    'disminuyen, así que un pedido que no cupo jamás cabrá después en ese mismo '
                    'lote. Y la aritmética de punto flotante necesita una tolerancia (EPS) en la '
                    'división entera: sin ella, 0,5 ÷ 0,1 puede devolver 4 en vez de 5.</div>',
                    unsafe_allow_html=True)

    with t4:
        st.markdown("### Temas de Producción III presentes en el método")
        st.dataframe(pd.DataFrame([
            ("Formación de lotes", "✅ Central", "Es el problema que resuelve el artículo"),
            ("Sistemas Flexibles de Manufactura", "✅ Central", "Contexto tecnológico completo"),
            ("Capacidad instalada", "✅ Central", "mⱼ × Pⱼ y mⱼ × Kⱼ son las dos capacidades"),
            ("Programación de producción", "✅ Alta", "Asignación de pedidos a periodos"),
            ("Secuenciación por fecha de entrega (EDD)", "✅ Alta", "Es el criterio del Paso 1"),
            ("Alistamiento y preparación", "✅ Alta", "Cada lote exige un alistamiento nuevo"),
            ("Utilización de máquinas", "✅ Alta", "Es la Tabla 4 del artículo"),
            ("Fraccionamiento de órdenes (lot splitting)", "✅ Media", "Un pedido puede partirse entre lotes"),
            ("Optimización heurística", "✅ Media", "Heurística constructiva, no exacta"),
            ("Investigación de Operaciones", "✅ Media", "Modelo de restricciones de fondo"),
        ], columns=["Tema", "Relevancia", "Descripción"]),
            hide_index=True, use_container_width=True)


# ══════════════════════════════════════════════════════════════
#  MÓDULO 2 — CONFIGURAR FMS
# ══════════════════════════════════════════════════════════════

def modulo_configurar():
    st.markdown('<div class="section-title">⚙️ Configuración del Sistema FMS</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("📂 Cargar caso del artículo", type="primary", use_container_width=True):
            st.session_state["cfg"] = caso_articulo()
            st.session_state["resultado"] = None
            st.session_state["cfg_ver"] = st.session_state.get("cfg_ver", 0) + 1
            st.rerun()
    with c2:
        st.markdown('<div class="alert-info">El botón llena todo con la Tabla 1 del artículo. '
                    'Es a la vez la demostración y la prueba de que el programa está bien: '
                    'ejecutándolo tal cual debe reproducir las Tablas 3 y 4 publicadas.</div>',
                    unsafe_allow_html=True)

    cfg = st.session_state.get("cfg") or caso_articulo()
    ver = st.session_state.get("cfg_ver", 0)   # cambia la key para refrescar los editores

    st.markdown("---")
    st.markdown("### 1. Tipos de máquina del sistema")
    st.caption("Una fila por tipo de máquina. Las capacidades por lote se calculan solas.")

    if not cfg.get("tipos"):
        cfg["tipos"] = [{"code": "A", "m": 1, "P": 12.0, "K": 2}]
    df_tipos = pd.DataFrame(cfg["tipos"]).rename(columns={
        "code": "Código", "m": "N° de máquinas (mⱼ)",
        "P": "Horas del turno (Pⱼ)", "K": "Portaherr. por máquina (Kⱼ)"})

    df_tipos = st.data_editor(
        df_tipos, num_rows="dynamic", use_container_width=True, hide_index=True,
        key=f"ed_tipos_{ver}",
        column_config={
            "Código": st.column_config.TextColumn(required=True, width="small"),
            "N° de máquinas (mⱼ)": st.column_config.NumberColumn(min_value=1, step=1, required=True),
            "Horas del turno (Pⱼ)": st.column_config.NumberColumn(min_value=0.0, step=0.5,
                                                                  format="%.2f", required=True),
            "Portaherr. por máquina (Kⱼ)": st.column_config.NumberColumn(min_value=1, step=1,
                                                                         required=True),
        })

    tipos_nuevos = []
    for _, r in df_tipos.iterrows():
        code = val_txt(r["Código"]).strip()
        if not code:
            continue
        tipos_nuevos.append({
            "code": code,
            "m": int(val_num(r["N° de máquinas (mⱼ)"], 1)) or 1,
            "P": val_num(r["Horas del turno (Pⱼ)"], 0.0),
            "K": int(val_num(r["Portaherr. por máquina (Kⱼ)"], 1)) or 1,
        })

    if not tipos_nuevos:
        st.markdown('<div class="alert-error">Define al menos un tipo de máquina para continuar.</div>',
                    unsafe_allow_html=True)
        return

    cols = st.columns(len(tipos_nuevos))
    for col, t in zip(cols, tipos_nuevos):
        col.markdown(
            f'<div class="metric-card"><div class="metric-label">Tipo {t["code"]} — por lote</div>'
            f'<div class="metric-value">{num(t["m"] * t["P"])} h</div>'
            f'<div style="font-size:0.8rem;color:#64748b;margin-top:4px;">'
            f'{t["m"] * t["K"]} espacios de herramienta</div></div>',
            unsafe_allow_html=True)

    codigos = [t["code"] for t in tipos_nuevos]

    st.markdown("---")
    st.markdown("### 2. Pedidos")
    st.caption("Una fila por pedido. El mismo tipo de parte puede aparecer en varios pedidos "
               "con tiempos distintos. Herramientas separadas por coma. "
               "Si el tiempo unitario en una máquina es 0, esa máquina se ignora por completo "
               "para ese pedido (tiempo y herramientas).")

    filas = []
    for p in cfg["pedidos"]:
        fila = {"Tipo de parte": p.get("parte", ""),
                "Tamaño de la orden (uᵢ)": p.get("size", 0),
                "Fecha de entrega (dᵢ)": p.get("due", 0)}
        for j in codigos:
            fila[f"h/und en {j}"] = float(p.get(f"t_{j}", 0.0) or 0.0)
            fila[f"Herramientas {j}"] = p.get(f"h_{j}", "") or ""
        filas.append(fila)

    colcfg = {
        "Tipo de parte": st.column_config.TextColumn(required=True, width="small"),
        "Tamaño de la orden (uᵢ)": st.column_config.NumberColumn(min_value=0, step=1, required=True),
        "Fecha de entrega (dᵢ)": st.column_config.NumberColumn(
            min_value=0, step=1, required=True,
            help="Día relativo entero: 0, 1, 2, 4… Si manejas fechas reales, conviértelas a día ordinal."),
    }
    for j in codigos:
        colcfg[f"h/und en {j}"] = st.column_config.NumberColumn(min_value=0.0, step=0.001, format="%.3f")
        colcfg[f"Herramientas {j}"] = st.column_config.TextColumn(
            help=f"Herramientas que la pieza necesita en la máquina {j}, separadas por coma.")

    df_ped = st.data_editor(pd.DataFrame(filas), num_rows="dynamic",
                            use_container_width=True, hide_index=True,
                            key=f"ed_pedidos_{ver}", column_config=colcfg)

    pedidos_nuevos = []
    for _, r in df_ped.iterrows():
        parte = val_txt(r["Tipo de parte"]).strip()
        if not parte:
            continue
        p = {"parte": parte,
             "size": int(val_num(r["Tamaño de la orden (uᵢ)"], 0)),
             "due": val_num(r["Fecha de entrega (dᵢ)"], 0)}
        for j in codigos:
            p[f"t_{j}"] = val_num(r.get(f"h/und en {j}"), 0.0)
            p[f"h_{j}"] = val_txt(r.get(f"Herramientas {j}"))
        pedidos_nuevos.append(p)

    st.markdown("---")
    if st.button("💾 Guardar configuración", type="primary"):
        st.session_state["cfg"] = {"tipos": tipos_nuevos, "pedidos": pedidos_nuevos}
        st.session_state["resultado"] = None
        st.success("Configuración guardada. Ve a 'Ejecutar Algoritmo'.")

    if not pedidos_nuevos:
        st.markdown('<div class="alert-warn">Agrega al menos un pedido.</div>',
                    unsafe_allow_html=True)
        return

    tipos, pedidos = cfg_a_objetos({"tipos": tipos_nuevos, "pedidos": pedidos_nuevos})
    errores, avisos = validar(tipos, pedidos)
    for e in errores:
        st.markdown(f'<div class="alert-error">🚨 {e}</div>', unsafe_allow_html=True)
    for a in avisos:
        st.markdown(f'<div class="alert-warn">⚠️ {a}</div>', unsafe_allow_html=True)
    if not errores and not avisos:
        st.markdown('<div class="alert-ok">✅ Los datos son factibles.</div>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  MÓDULO 3 — EJECUTAR
# ══════════════════════════════════════════════════════════════

def texto_decision(r):
    d = r["detalle"]
    partes = []
    for j, info in d["tiempo"].items():
        partes.append(f"En **{j}** quedaban {num(info['libre'], 4)} h libres y cada unidad "
                      f"consume {num(info['unitario'], 4)} h → caben {info['caben']} unidades.")
    ignoradas = [j for j, v in d["herramientas"].items() if v is None]
    if ignoradas:
        partes.append(f"La(s) máquina(s) **{', '.join(ignoradas)}** se ignoran: "
                      f"el tiempo unitario de la pieza allí es 0.")
    nuevas = {j: v["nuevas"] for j, v in d["herramientas"].items() if v and v["nuevas"]}
    if nuevas:
        partes.append("Herramientas nuevas cargadas: " +
                      "; ".join(f"{j} → {', '.join(v)}" for j, v in nuevas.items()) + ".")
    else:
        partes.append("No se cargó ninguna herramienta nueva: todas ya estaban en el lote "
                      "(costo cero).")
    partes.append(f"**q = mínimo({r['pendiente_antes']} pendientes"
                  + "".join(f", {i['caben']}" for i in d["tiempo"].values())
                  + f") = {r['asignadas']}** — manda {d['restriccion']}.")
    return "  \n".join(partes)


def texto_rechazo(m):
    d = m["detalle"]
    if d["bloqueo_herr"]:
        b = d["bloqueo_herr"]
        return (f"Rechazado por **herramientas** en {b['tipo']}: ya hay {b['cargadas']} "
                f"cargadas de {b['capacidad']} espacios y necesita "
                f"{len(b['nuevas'])} nueva(s) ({', '.join(b['nuevas'])}).")
    apretadas = [f"{j} (quedan {num(i['libre'], 4)} h y una unidad pide {num(i['unitario'], 4)} h)"
                 for j, i in d["tiempo"].items() if i["caben"] == 0]
    return "Rechazado por **tiempo**: no cabe ni una unidad en " + ", ".join(apretadas) + "."


def modulo_ejecutar():
    st.markdown('<div class="section-title">▶ Ejecutar el Algoritmo de Formación de Lotes</div>',
                unsafe_allow_html=True)

    if not st.session_state.get("cfg"):
        st.markdown('<div class="alert-warn">⚠️ Primero configura el FMS.</div>',
                    unsafe_allow_html=True)
        return

    tipos, pedidos = cfg_a_objetos(st.session_state["cfg"])
    errores, avisos = validar(tipos, pedidos)

    cols = st.columns(len(tipos) + 1)
    cols[0].markdown(f'<div class="metric-card"><div class="metric-label">Pedidos</div>'
                     f'<div class="metric-value">{len(pedidos)}</div></div>',
                     unsafe_allow_html=True)
    for col, (j, mt) in zip(cols[1:], tipos.items()):
        col.markdown(
            f'<div class="metric-card"><div class="metric-label">Tipo {j} por lote</div>'
            f'<div class="metric-value">{num(mt.cap_tiempo)} h</div>'
            f'<div style="font-size:0.8rem;color:#64748b;margin-top:4px;">'
            f'{mt.cap_herr} espacios</div></div>', unsafe_allow_html=True)

    if errores:
        for e in errores:
            st.markdown(f'<div class="alert-error">🚨 {e}</div>', unsafe_allow_html=True)
        return
    for a in avisos:
        st.markdown(f'<div class="alert-warn">⚠️ {a}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Paso 1 — Fila de espera ordenada por fecha de entrega")
    st.dataframe(tabla2(pedidos, tipos), hide_index=True, use_container_width=True)
    st.caption("Fecha ascendente; los empates se rompen por mayor tiempo total de producción.")

    st.markdown("---")
    if st.button("▶ Ejecutar el algoritmo", type="primary", use_container_width=True):
        try:
            lotes, bitacora = ejecutar(pedidos, tipos)
            st.session_state["resultado"] = {"lotes": lotes, "bitacora": bitacora, "tipos": tipos}
            st.success(f"Listo: {len(bitacora)} iteraciones en {len(lotes)} lote(s).")
        except InfactibilidadError as e:
            st.session_state["resultado"] = None
            st.markdown(f'<div class="alert-error">🚨 {e}</div>', unsafe_allow_html=True)

    res = st.session_state.get("resultado")
    if not res:
        return

    lotes, bitacora, tipos = res["lotes"], res["bitacora"], res["tipos"]

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Paso 2 — Iteración por iteración")

    for l in lotes:
        st.markdown(f'<div class="lote-header">📦 Lote {l.indice} — alistamiento en cero</div>',
                    unsafe_allow_html=True)
        for r in [x for x in bitacora if x["lote"] == l.indice]:
            etiqueta = f"{r['parte']} ({r['asignadas']}/{r['tam_original']})"
            titulo = f"Iteración {r['iteracion']} · parte {etiqueta}"
            with st.expander(titulo, expanded=(r["iteracion"] == 1)):
                st.markdown(texto_decision(r))
                if r["fraccionado"]:
                    st.markdown(f'<div class="decision-frac">✂️ Se FRACCIONA: '
                                f'{r["asignadas"]} de {r["pendiente_antes"]} unidades en este lote. '
                                f'Quedan {r["resto"]} pendientes para el siguiente.</div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="decision-ok">✅ Se asigna COMPLETO: '
                                f'{r["asignadas"]} unidades.</div>', unsafe_allow_html=True)

                estado = []
                for j, mt in tipos.items():
                    estado.append({
                        "Tipo de máquina": j,
                        "Consumido en la iteración (h)": num(r["consumo"][j], 4),
                        "Tiempo acumulado (h)": num(r["t_acum"][j], 4),
                        "Tiempo restante (h)": num(mt.cap_tiempo - r["t_acum"][j], 4),
                        "Herramientas cargadas": ", ".join(r["herr_acum"][j]) or "—",
                        "Portaherr. restantes": mt.cap_herr - len(r["herr_acum"][j]),
                    })
                st.dataframe(pd.DataFrame(estado), hide_index=True, use_container_width=True)

                fig = lineas_estado(bitacora, r["iteracion"], tipos)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

        if l.motivo_cierre:
            st.markdown(f"**Barrido antes de cerrar el Lote {l.indice}** — "
                        f"el lote no se cierra sin intentar con los demás pedidos:")
            for m in l.motivo_cierre:
                st.markdown(f'<div class="decision-no">🚫 <b>{m["parte"]}</b> '
                            f'({m["pendientes"]} unidades pendientes) — {texto_rechazo(m)}</div>',
                            unsafe_allow_html=True)
            st.caption(f"Ningún pedido pendiente pudo entrar → se cierra el Lote {l.indice}."
                       + (f" Se abre el Lote {l.indice + 1}." if l.indice < len(lotes) else ""))
        st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="alert-ok">✅ No quedan pedidos pendientes. El método terminó.</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  MÓDULO 4 — RESULTADOS
# ══════════════════════════════════════════════════════════════

def modulo_resultados():
    st.markdown('<div class="section-title">📈 Resultados y Análisis</div>',
                unsafe_allow_html=True)

    res = st.session_state.get("resultado")
    if not res:
        st.markdown('<div class="alert-warn">⚠️ Primero ejecuta el algoritmo.</div>',
                    unsafe_allow_html=True)
        return

    lotes, bitacora, tipos = res["lotes"], res["bitacora"], res["tipos"]

    c = st.columns(3)
    c[0].markdown(f'<div class="metric-card"><div class="metric-label">Lotes formados</div>'
                  f'<div class="metric-value">{len(lotes)}</div></div>', unsafe_allow_html=True)
    c[1].markdown(f'<div class="metric-card"><div class="metric-label">Iteraciones</div>'
                  f'<div class="metric-value">{len(bitacora)}</div></div>', unsafe_allow_html=True)
    frac = sum(1 for r in bitacora if r["fraccionado"])
    c[2].markdown(f'<div class="metric-card"><div class="metric-label">Pedidos fraccionados</div>'
                  f'<div class="metric-value {"warn" if frac else "ok"}">{frac}</div></div>',
                  unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Tabla 3 — Resumen de las iteraciones")
    st.dataframe(tabla3(bitacora, tipos), hide_index=True, use_container_width=True)
    st.caption("Los tiempos y las herramientas son acumulados dentro del lote: la foto justo "
               "después de esa asignación. La notación d (2/10) significa unidades asignadas "
               "sobre el tamaño original del pedido. Las herramientas se listan en orden de "
               "carga, no alfabético.")

    st.markdown("### Tabla 4 — Porcentaje de utilización de las máquinas")
    st.dataframe(tabla4(lotes, tipos), hide_index=True, use_container_width=True)
    st.markdown('<div class="formula-box">% utilización (lote, j) = '
                'Tiempo acumulado del lote en j ÷ ( mⱼ × Pⱼ ) × 100</div>',
                unsafe_allow_html=True)

    fig = barras_utilizacion(lotes, tipos)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Líneas de tiempo y de portaherramientas")
    st.caption("Cada barra de tiempo tiene el largo de la capacidad del tipo de máquina; "
               "cada asignación agrega un segmento. La barra de herramientas tiene una celda "
               "por espacio disponible.")
    it = st.slider("Iteración", 1, len(bitacora), len(bitacora))
    fila = next(r for r in bitacora if r["iteracion"] == it)
    st.markdown(f"**Iteración {it}** · Lote {fila['lote']} · parte "
                f"{fila['parte']} ({fila['asignadas']}/{fila['tam_original']})")
    fig = lineas_estado(bitacora, it, tipos)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Holgura al cerrar cada lote")
    holg = []
    for l in lotes:
        fila = {"Lote": l.indice}
        for j, mt in tipos.items():
            fila[f"Horas libres en {j}"] = num(mt.cap_tiempo - l.used_time[j], 4)
            fila[f"Espacios libres en {j}"] = mt.cap_herr - len(l.tools[j])
        holg.append(fila)
    st.dataframe(pd.DataFrame(holg), hide_index=True, use_container_width=True)
    st.caption("El artículo señala que el espacio libre del último lote sirve para recibir "
               "nuevas solicitudes.")

    with st.expander("📌 Erratas del artículo (léelas antes de la sustentación)"):
        st.markdown("""
**1. Herramientas de la parte e.** La Tabla 1 dice que la parte e requiere A5 y B3, y el texto
de la Iteración 6 lo confirma. Pero la Tabla 3 y las figuras del Lote 2 muestran A1, A3 y B2, B5:
es una transposición de dígitos al elaborar la tabla. Un programa fiel a los datos de entrada
produce **A1, A5** y **B2, B3**, que es lo correcto. No coincide carácter por carácter con la
Tabla 3 impresa en las filas 6 y 7, y eso está bien. No altera ningún número de la Tabla 4.

**2. Pies de figura corridos** una posición en la página 74: la figura rotulada "Iteración 5"
muestra los acumulados 2,0 y 2,4, que corresponden a la Iteración 6. Solo afecta la lectura del
artículo, no el modelo.

**3. La parte a aparece en dos pedidos con tiempos unitarios distintos** (0,1 / 0,3 y 0,3 / 0,2)
pese a ser el mismo tipo de parte. Por eso en este programa los tiempos viven a nivel de
**pedido**, no de tipo de parte.
        """)

    seccion_analisis_grafico(lotes, bitacora, tipos)

# ══════════════════════════════════════════════════════════════
#  MÓDULO 5 — REPORTES
# ══════════════════════════════════════════════════════════════

def modulo_reportes():
    st.markdown('<div class="section-title">📋 Reportes y Exportación</div>',
                unsafe_allow_html=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")

    st.markdown("### Configuración")
    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.get("cfg"):
            st.download_button(
                "⬇️ Descargar configuración (.json)",
                json.dumps(st.session_state["cfg"], indent=2, ensure_ascii=False).encode("utf-8"),
                f"fms_config_{ts}.json", "application/json", use_container_width=True)
    with c2:
        up = st.file_uploader("Cargar configuración guardada (.json)", type=["json"])
        if up:
            try:
                st.session_state["cfg"] = json.load(up)
                st.session_state["resultado"] = None
                st.session_state["cfg_ver"] = st.session_state.get("cfg_ver", 0) + 1
                st.success("Configuración cargada. Ve a 'Ejecutar Algoritmo'.")
            except Exception as e:
                st.error(f"No se pudo leer el archivo: {e}")

    res = st.session_state.get("resultado")
    if not res:
        st.markdown('<div class="alert-warn">⚠️ Ejecuta el algoritmo para generar los reportes '
                    'de resultados.</div>', unsafe_allow_html=True)
        return

    lotes, bitacora, tipos = res["lotes"], res["bitacora"], res["tipos"]
    _, pedidos = cfg_a_objetos(st.session_state["cfg"])

    st.markdown("---")
    t1, t2, t3, t4 = st.tabs(["Tabla 2 — Orden", "Tabla 3 — Iteraciones",
                              "Tabla 4 — Utilización", "Asignación por lote"])

    with t1:
        df = tabla2(pedidos, tipos)
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.download_button("⬇️ Descargar (.csv)",
                           df.to_csv(index=False).encode("utf-8-sig"),
                           f"fms_tabla2_orden_{ts}.csv", "text/csv", type="primary")

    with t2:
        df = tabla3(bitacora, tipos, formato=False)
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.download_button("⬇️ Descargar (.csv)",
                           df.to_csv(index=False).encode("utf-8-sig"),
                           f"fms_tabla3_iteraciones_{ts}.csv", "text/csv", type="primary")

    with t3:
        df = tabla4(lotes, tipos, formato=False)
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.download_button("⬇️ Descargar (.csv)",
                           df.to_csv(index=False).encode("utf-8-sig"),
                           f"fms_tabla4_utilizacion_{ts}.csv", "text/csv", type="primary")

    with t4:
        filas = []
        for r in bitacora:
            fila = {"Lote": r["lote"], "Iteración": r["iteracion"], "Parte": r["parte"],
                    "Unidades asignadas": r["asignadas"], "Tamaño original": r["tam_original"],
                    "¿Fraccionado?": "Sí" if r["fraccionado"] else "No"}
            for j in tipos:
                fila[f"Horas consumidas en {j}"] = r["consumo"][j]
                fila[f"Herramientas acum. {j}"] = ", ".join(r["herr_acum"][j])
            filas.append(fila)
        df = pd.DataFrame(filas)
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.download_button("⬇️ Descargar (.csv)",
                           df.to_csv(index=False).encode("utf-8-sig"),
                           f"fms_asignaciones_{ts}.csv", "text/csv", type="primary")

    st.markdown("---")
    st.markdown("### Exportar resultados completos (.json)")
    st.caption("El artículo señala que estos resultados son el insumo de la Heurística de Carga. "
               "La salida serializable prepara ese siguiente paso.")
    salida = {
        "tipos": {j: {"m": mt.n_machines, "P": mt.hours_per_machine, "K": mt.holders_per_machine,
                      "cap_tiempo": mt.cap_tiempo, "cap_herr": mt.cap_herr}
                  for j, mt in tipos.items()},
        "iteraciones": [{k: v for k, v in r.items() if k != "detalle"} for r in bitacora],
        "lotes": [{"lote": l.indice, "tiempo_usado": l.used_time,
                   "herramientas": l.tools} for l in lotes],
    }
    st.download_button("⬇️ Descargar resultados (.json)",
                       json.dumps(salida, indent=2, ensure_ascii=False).encode("utf-8"),
                       f"fms_resultados_{ts}.json", "application/json")


# ══════════════════════════════════════════════════════════════
#  MÓDULO 6 — REFERENCIAS
# ══════════════════════════════════════════════════════════════

def modulo_referencias():
    st.markdown('<div class="section-title">📚 Referencias Bibliográficas</div>',
                unsafe_allow_html=True)
    st.markdown("Todas las referencias están en formato **APA 7.ª edición**.")
    st.markdown("---")

    st.markdown("### 📄 Artículo base de la aplicación")
    st.markdown("""
    <div class="ref-card" style="border-left:4px solid #dc2626;">
    Medina Varela, P. D., Cruz Trejos, E. A., &amp; Restrepo Correa, J. H. (2009).
    Problema de formación de lotes de fabricación en un sistema de manufactura flexible:
    Heurística de selección de partes.
    <i>El Hombre y la Máquina, 32</i>, 68–79.
    Universidad Tecnológica de Pereira, Pereira, Colombia.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📖 Libros y manuales de referencia")
    for r in [
        "Groover, M. P. (2007). <i>Automation, production systems, and computer-integrated manufacturing</i> (3.ª ed.). Pearson Prentice Hall.",
        "Chase, R. B., Aquilano, N. J., &amp; Jacobs, F. R. (2005). <i>Administración de producción y operaciones: manufactura y servicios</i> (10.ª ed.). McGraw-Hill.",
        "Sipper, D., &amp; Bulfin, R. L. (1998). <i>Planeación y control de la producción</i>. McGraw-Hill.",
        "Hillier, F. S., &amp; Lieberman, G. J. (2021). <i>Introduction to operations research</i> (11.ª ed.). McGraw-Hill.",
        "Askin, R. G., &amp; Standridge, C. R. (1993). <i>Modeling and analysis of manufacturing systems</i>. John Wiley &amp; Sons.",
    ]:
        st.markdown(f'<div class="ref-card">{r}</div>', unsafe_allow_html=True)

    st.markdown("### 📰 Artículos científicos relacionados")
    for r in [
        "Stecke, K. E. (1983). Formulation and solution of nonlinear integer production planning problems for flexible manufacturing systems. <i>Management Science, 29</i>(3), 273–288. https://doi.org/10.1287/mnsc.29.3.273",
        "Kiran, A. S., &amp; Tansel, B. C. (1991). Scheduling in flexible manufacturing systems: A review. <i>International Journal of Production Research, 29</i>(7), 1469–1495. https://doi.org/10.1080/00207549108948020",
        "Kusiak, A. (1985). Flexible manufacturing systems: A structural approach. <i>International Journal of Production Research, 23</i>(6), 1057–1073. https://doi.org/10.1080/00207548508904768",
        "Raj, T., Shankar, R., &amp; Suhaib, M. (2008). An ISM approach for modelling the enablers of flexible manufacturing system: The case for India. <i>International Journal of Production Research, 46</i>(24), 6883–6912.",
    ]:
        st.markdown(f'<div class="ref-card">{r}</div>', unsafe_allow_html=True)

    st.markdown("### 🌐 Software")
    st.markdown("""
    <div class="ref-card">
    Universidad Tecnológica de Pereira. (2026). <i>FMS.lab: implementación de la heurística de
    selección de partes para formación de lotes en sistemas de manufactura flexible</i>
    [Software]. Desarrollado con Python y Streamlit. Producción III — Ingeniería Industrial.
    </div>
    """, unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════
#  MÓDULO ADICIONAL — ANÁLISIS GRÁFICO INTEGRAL
#  Bloque 100 % aditivo: no modifica ninguna función existente.
#  Reutiliza EPS, PALETA, GRIS_BORDE, num(), tabla2/3/4 y los objetos
#  MachineType / Lot que ya produce el algoritmo.
#
#  INTEGRACIÓN: pegar este bloque justo ANTES de la sección
#  "APP PRINCIPAL" y agregar UNA sola línea al final de
#  modulo_resultados():   seccion_analisis_grafico(lotes, bitacora, tipos)
# ══════════════════════════════════════════════════════════════

AG_FONDO = "#f8fafc"
AG_LIBRE = "#eef2f7"
AG_ROJO = "#dc2626"
AG_AZUL = "#1e3a5f"


# ──────────────────────────────────────────────────────────────
#  1. DATOS DERIVADOS (sin recalcular la heurística)
# ──────────────────────────────────────────────────────────────

def ag_colores(bitacora):
    """Un color estable por pedido (oid), con la paleta que ya usa la app."""
    oids = []
    for r in bitacora:
        if r["oid"] not in oids:
            oids.append(r["oid"])
    return {oid: PALETA[i % len(PALETA)] for i, oid in enumerate(oids)}


def ag_etiqueta(r):
    return f"{r['parte']} ({r['asignadas']}/{r['tam_original']})"


def ag_limitante(lote, tipos):
    """Recurso que más se satura en el lote: el equivalente honesto del
    'cuello de botella' en esta heurística. Devuelve (tipo, recurso, %)."""
    mejor_j, mejor_rec, mejor_v = None, "", -1.0
    for j, mt in tipos.items():
        ut = lote.used_time[j] / mt.cap_tiempo * 100 if mt.cap_tiempo else 0.0
        uh = len(lote.tools[j]) / mt.cap_herr * 100 if mt.cap_herr else 0.0
        for v, rec in ((ut, "tiempo"), (uh, "portaherramientas")):
            if v > mejor_v:
                mejor_j, mejor_rec, mejor_v = j, rec, v
    return mejor_j, mejor_rec, mejor_v


def ag_tablas(lotes, bitacora, tipos):
    """DataFrames que alimentan los gráficos y las descargas."""
    # --- Lotes ---
    f_lotes = []
    for l in lotes:
        j_lim, rec_lim, v_lim = ag_limitante(l, tipos)
        reg = [r for r in bitacora if r["lote"] == l.indice]
        fila = {
            "Lote": l.indice,
            "Pedidos asignados": len(reg),
            "Unidades fabricadas": sum(r["asignadas"] for r in reg),
            "Partes": ", ".join(dict.fromkeys(r["parte"] for r in reg)),
            "Fraccionamientos": sum(1 for r in reg if r["fraccionado"]),
        }
        for j, mt in tipos.items():
            fila[f"Horas usadas {j}"] = round(l.used_time[j], 4)
            fila[f"Capacidad {j} (h)"] = mt.cap_tiempo
            fila[f"% utilización {j}"] = round(
                l.used_time[j] / mt.cap_tiempo * 100 if mt.cap_tiempo else 0, 2)
            fila[f"Herramientas {j}"] = ", ".join(l.tools[j])
            fila[f"Portaherr. usados {j}"] = f"{len(l.tools[j])}/{mt.cap_herr}"
        fila["Recurso limitante"] = f"{rec_lim} en {j_lim} ({round(v_lim, 2)} %)"
        f_lotes.append(fila)

    # --- Máquinas ---
    f_maq = []
    for j, mt in tipos.items():
        usado = sum(l.used_time[j] for l in lotes)
        capac = mt.cap_tiempo * len(lotes)
        herr = sorted({h for l in lotes for h in l.tools[j]})
        f_maq.append({
            "Tipo de máquina": j,
            "N° de máquinas (mj)": mt.n_machines,
            "Horas del turno (Pj)": mt.hours_per_machine,
            "Portaherr. por máquina (Kj)": mt.holders_per_machine,
            "Capacidad por lote (h)": mt.cap_tiempo,
            "Espacios de herramienta por lote": mt.cap_herr,
            "Horas usadas en total": round(usado, 4),
            "Capacidad total (todos los lotes)": round(capac, 4),
            "% utilización global": round(usado / capac * 100 if capac else 0, 2),
            "Herramientas distintas usadas": ", ".join(herr),
        })

    # --- Asignaciones / Gantt ---
    f_gantt, cursores = [], {}
    for r in bitacora:
        for j, mt in tipos.items():
            dur = r["consumo"].get(j, 0.0)
            if dur <= EPS:
                continue
            clave = (r["lote"], j)
            ini = cursores.get(clave, 0.0)
            f_gantt.append({
                "Lote": r["lote"], "Iteración": r["iteracion"], "Tipo de máquina": j,
                "Parte": r["parte"], "Pedido (oid)": r["oid"],
                "Unidades": r["asignadas"], "Tamaño original": r["tam_original"],
                "Inicio (h)": round(ini, 4), "Duración (h)": round(dur, 4),
                "Fin (h)": round(ini + dur, 4),
                "Capacidad del tipo (h)": mt.cap_tiempo,
            })
            cursores[clave] = ini + dur

    # --- Iteraciones ---
    f_iter = []
    for r in bitacora:
        fila = {
            "Iteración": r["iteracion"], "Lote": r["lote"], "Parte": r["parte"],
            "Unidades asignadas": r["asignadas"], "Tamaño original": r["tam_original"],
            "¿Fraccionado?": "Sí" if r["fraccionado"] else "No",
            "Pendiente después": r["resto"],
            "Restricción que mandó": r["detalle"].get("restriccion", ""),
        }
        for j, mt in tipos.items():
            fila[f"Horas consumidas {j}"] = round(r["consumo"].get(j, 0.0), 4)
            fila[f"Tiempo acum. {j}"] = round(r["t_acum"][j], 4)
            fila[f"% acum. {j}"] = round(
                r["t_acum"][j] / mt.cap_tiempo * 100 if mt.cap_tiempo else 0, 2)
            fila[f"Portaherr. ocupados {j}"] = len(r["herr_acum"][j])
            fila[f"Herramientas acum. {j}"] = ", ".join(r["herr_acum"][j])
        f_iter.append(fila)

    # --- Rechazos (barrido antes de cerrar cada lote) ---
    f_rech = []
    for l in lotes:
        for m in l.motivo_cierre:
            d = m["detalle"]
            if d.get("bloqueo_herr"):
                b = d["bloqueo_herr"]
                causa = (f"Portaherramientas en {b['tipo']}: {b['cargadas']}/{b['capacidad']} "
                         f"ocupados y pedía {len(b['nuevas'])} nueva(s)")
            else:
                aprt = [f"{j} (quedan {round(i['libre'], 4)} h, una unidad pide {i['unitario']} h)"
                        for j, i in d.get("tiempo", {}).items() if i["caben"] == 0]
                causa = "Tiempo: no cabe ni una unidad en " + ", ".join(aprt) if aprt else "Sin espacio"
            f_rech.append({"Lote": l.indice, "Parte rechazada": m["parte"],
                           "Unidades pendientes": m["pendientes"], "Causa": causa})

    return (pd.DataFrame(f_lotes), pd.DataFrame(f_maq), pd.DataFrame(f_gantt),
            pd.DataFrame(f_iter), pd.DataFrame(f_rech))


def ag_resumen(lotes, bitacora, tipos):
    """Cifras del encabezado del dashboard."""
    utils = []
    for l in lotes:
        for j, mt in tipos.items():
            utils.append(l.used_time[j] / mt.cap_tiempo * 100 if mt.cap_tiempo else 0)
    peor_j, peor_rec, peor_v, peor_lote = None, "", -1.0, None
    for l in lotes:
        j, rec, v = ag_limitante(l, tipos)
        if v > peor_v:
            peor_j, peor_rec, peor_v, peor_lote = j, rec, v, l.indice
    return {
        "lotes": len(lotes),
        "tipos": len(tipos),
        "maquinas": sum(mt.n_machines for mt in tipos.values()),
        "iteraciones": len(bitacora),
        "fraccionamientos": sum(1 for r in bitacora if r["fraccionado"]),
        "unidades": sum(r["asignadas"] for r in bitacora),
        "util_media": sum(utils) / len(utils) if utils else 0.0,
        "limitante": (peor_j, peor_rec, peor_v, peor_lote),
    }


# ──────────────────────────────────────────────────────────────
#  2. GRÁFICOS
# ──────────────────────────────────────────────────────────────

def ag_estilo(ax, titulo="", xlab="", ylab=""):
    ax.set_facecolor(AG_FONDO)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRIS_BORDE)
    ax.spines["bottom"].set_color(GRIS_BORDE)
    ax.tick_params(colors="#64748b", labelsize=9)
    if titulo:
        ax.set_title(titulo, fontweight="bold", color=AG_AZUL, fontsize=12, pad=12)
    if xlab:
        ax.set_xlabel(xlab, color=AG_AZUL, fontsize=10)
    if ylab:
        ax.set_ylabel(ylab, color=AG_AZUL, fontsize=10)


def ag_g1_composicion(lotes, bitacora, colores):
    """Gráfico 1 — Qué pedidos y cuántas unidades componen cada lote."""
    fig, ax = plt.subplots(figsize=(11, max(2.4, 0.72 * len(lotes) + 1.7)), facecolor="white")
    total_max = max((sum(r["asignadas"] for r in bitacora if r["lote"] == l.indice)
                     for l in lotes), default=1) or 1
    for l in lotes:
        base = 0
        for r in [x for x in bitacora if x["lote"] == l.indice]:
            ax.barh(l.indice, r["asignadas"], left=base, height=0.62,
                    color=colores[r["oid"]], edgecolor="white", linewidth=1.6, zorder=3)
            if r["asignadas"] / total_max > 0.07:
                ax.text(base + r["asignadas"] / 2, l.indice, ag_etiqueta(r),
                        ha="center", va="center", color="white", fontsize=8.5,
                        fontweight="bold", zorder=4)
            base += r["asignadas"]
        ax.text(base + total_max * 0.012, l.indice, f"{base} und.",
                va="center", fontsize=9, fontfamily="monospace", color=AG_AZUL, zorder=4)
    ax.set_yticks([l.indice for l in lotes])
    ax.set_yticklabels([f"Lote {l.indice}" for l in lotes], fontsize=10, color=AG_AZUL)
    ax.invert_yaxis()
    ax.set_xlim(0, total_max * 1.16)
    ax.grid(True, axis="x", color="#e2e8f0", linestyle="--", alpha=0.9, zorder=1)
    ag_estilo(ax, "Gráfico 1 — Composición de cada lote (unidades por pedido)",
              "Unidades fabricadas")
    fig.tight_layout()
    return fig


def ag_g2_gantt(lotes, bitacora, tipos, colores):
    """Gráfico 2 — Diagrama de Gantt: tiempo en el eje X, lote y máquina en el eje Y."""
    filas = [(l.indice, j) for l in lotes for j in tipos]
    cap_max = max(mt.cap_tiempo for mt in tipos.values()) or 1
    fig, ax = plt.subplots(figsize=(11, max(2.6, 0.52 * len(filas) + 1.9)), facecolor="white")

    cursores = {}
    for idx, (li, j) in enumerate(filas):
        mt = tipos[j]
        y = len(filas) - 1 - idx
        ax.broken_barh([(0, mt.cap_tiempo)], (y - 0.33, 0.66), facecolors=AG_LIBRE,
                       edgecolor=GRIS_BORDE, linewidth=0.9, zorder=2)
        for r in [x for x in bitacora if x["lote"] == li]:
            w = r["consumo"].get(j, 0.0)
            if w <= EPS:
                continue
            ini = cursores.get((li, j), 0.0)
            ax.broken_barh([(ini, w)], (y - 0.33, 0.66), facecolors=colores[r["oid"]],
                           edgecolor="white", linewidth=1.3, zorder=3)
            if w / cap_max > 0.055:
                ax.text(ini + w / 2, y, r["parte"], ha="center", va="center",
                        color="white", fontsize=8.5, fontweight="bold", zorder=4)
            cursores[(li, j)] = ini + w
        usado = cursores.get((li, j), 0.0)
        ax.text(cap_max * 1.015, y, f"{num(usado)} / {num(mt.cap_tiempo)} h",
                va="center", fontsize=8.5, fontfamily="monospace", color=AG_AZUL)
        if abs(mt.cap_tiempo - cap_max) > EPS:
            ax.plot([mt.cap_tiempo, mt.cap_tiempo], [y - 0.4, y + 0.4],
                    color=GRIS_BORDE, linewidth=1.4, zorder=4)

    ax.set_yticks(list(range(len(filas))))
    ax.set_yticklabels([f"Lote {li} · Máq. {j}" for li, j in reversed(filas)],
                       fontsize=9.5, color=AG_AZUL)
    ax.set_xlim(0, cap_max * 1.16)
    ax.set_ylim(-0.7, len(filas) - 0.3)
    ax.grid(True, axis="x", color="#e2e8f0", linestyle="--", alpha=0.9, zorder=1)
    ag_estilo(ax, "Gráfico 2 — Gantt: ocupación de cada tipo de máquina en cada lote",
              "Horas del periodo (bolsa de tiempo del tipo de máquina)")
    fig.tight_layout()
    return fig


def ag_g3_cargas(lotes, tipos):
    """Gráfico 3 — Cargas comparadas y recurso limitante de cada lote."""
    fig, axes = plt.subplots(1, 2, figsize=(11, max(3.0, 0.42 * len(lotes) * len(tipos) + 2.4)),
                             facecolor="white")
    datos = [
        ("Tiempo de máquina",
         lambda l, j, mt: l.used_time[j] / mt.cap_tiempo * 100 if mt.cap_tiempo else 0),
        ("Portaherramientas",
         lambda l, j, mt: len(l.tools[j]) / mt.cap_herr * 100 if mt.cap_herr else 0),
    ]
    for ax, (titulo, f) in zip(axes, datos):
        ancho = 0.8 / max(len(tipos), 1)
        for k, (j, mt) in enumerate(tipos.items()):
            xs = [i + k * ancho for i in range(len(lotes))]
            ys = [f(l, j, mt) for l in lotes]
            limites = [ag_limitante(l, tipos) for l in lotes]
            bordes = [AG_ROJO if (lm[0] == j and
                                  lm[1] == ("tiempo" if "Tiempo" in titulo else "portaherramientas"))
                      else "white" for lm in limites]
            grosor = [2.4 if b == AG_ROJO else 1.4 for b in bordes]
            barras = ax.bar(xs, ys, width=ancho, label=f"Máquina {j}",
                            color=PALETA[k % len(PALETA)], zorder=3)
            for b, col, g in zip(barras, bordes, grosor):
                b.set_edgecolor(col)
                b.set_linewidth(g)
            for b, v in zip(barras, ys):
                ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f}%".replace(".", ","),
                        ha="center", va="bottom", fontsize=8, fontfamily="monospace",
                        color="#374151")
        ax.set_xticks([i + ancho * (len(tipos) - 1) / 2 for i in range(len(lotes))])
        ax.set_xticklabels([f"Lote {l.indice}" for l in lotes], fontsize=9.5)
        ax.set_ylim(0, 118)
        ax.axhline(100, color=GRIS_BORDE, linestyle="--", linewidth=1.2, zorder=2)
        ax.grid(True, axis="y", color="#e2e8f0", linestyle="--", alpha=0.9, zorder=1)
        ag_estilo(ax, titulo, "", "% de ocupación")
        ax.legend(fontsize=8.5, framealpha=0.95, facecolor="white", edgecolor="#e2e8f0")
    fig.suptitle("Gráfico 3 — Carga por lote  ·  borde rojo = recurso limitante del lote",
                 fontweight="bold", color=AG_AZUL, fontsize=12, y=1.0)
    fig.tight_layout()
    return fig


def ag_g4_evolucion(lotes, bitacora, tipos):
    """Gráfico 4 — Evolución del consumo de tiempo iteración por iteración."""
    fig, ax = plt.subplots(figsize=(11, 4.0), facecolor="white")
    its = [r["iteracion"] for r in bitacora]

    for l in lotes:
        reg = [r["iteracion"] for r in bitacora if r["lote"] == l.indice]
        if not reg:
            continue
        ax.axvspan(min(reg) - 0.5, max(reg) + 0.5,
                   color="#e0e7ff" if l.indice % 2 else "#f1f5f9", alpha=0.55, zorder=1)
        ax.text((min(reg) + max(reg)) / 2, 108, f"Lote {l.indice}", ha="center",
                fontsize=9.5, fontweight="bold", color=AG_AZUL, zorder=5)

    for k, (j, mt) in enumerate(tipos.items()):
        xs, ys, lote_prev = [], [], None
        for r in bitacora:
            if lote_prev is not None and r["lote"] != lote_prev:
                xs.append(None)   # corta la línea: el lote nuevo arranca en cero
                ys.append(None)
            xs.append(r["iteracion"])
            ys.append(r["t_acum"][j] / mt.cap_tiempo * 100 if mt.cap_tiempo else 0)
            lote_prev = r["lote"]
        ax.plot(xs, ys, marker="o", markersize=6, linewidth=2.2,
                color=PALETA[k % len(PALETA)], label=f"Máquina {j}", zorder=4)

    for r in bitacora:
        if r["fraccionado"]:
            ax.annotate("fracción", (r["iteracion"], 4), fontsize=8, color="#92400e",
                        ha="center", zorder=5)

    ax.axhline(100, color=AG_ROJO, linestyle="--", linewidth=1.3, zorder=3)
    ax.text(its[-1] if its else 0, 101.5, "capacidad del lote", ha="right",
            fontsize=8.5, color=AG_ROJO)
    ax.set_xticks(its)
    ax.set_ylim(0, 118)
    ax.grid(True, axis="y", color="#e2e8f0", linestyle="--", alpha=0.9, zorder=2)
    ag_estilo(ax, "Gráfico 4 — Evolución del tiempo acumulado por iteración",
              "Iteración de la heurística", "% de la capacidad del lote")
    ax.legend(fontsize=9, framealpha=0.95, facecolor="white", edgecolor="#e2e8f0", loc="lower right")
    fig.tight_layout()
    return fig


def ag_g5_portaherramientas(lotes, bitacora, tipos):
    """Gráfico 5 — Ocupación de los portaherramientas iteración por iteración."""
    fig, ax = plt.subplots(figsize=(11, 3.8), facecolor="white")
    its = [r["iteracion"] for r in bitacora]

    for l in lotes:
        reg = [r["iteracion"] for r in bitacora if r["lote"] == l.indice]
        if not reg:
            continue
        ax.axvspan(min(reg) - 0.5, max(reg) + 0.5,
                   color="#e0e7ff" if l.indice % 2 else "#f1f5f9", alpha=0.55, zorder=1)

    cap_max = max(mt.cap_herr for mt in tipos.values()) or 1
    for k, (j, mt) in enumerate(tipos.items()):
        xs, ys, lote_prev = [], [], None
        for r in bitacora:
            if lote_prev is not None and r["lote"] != lote_prev:
                xs.append(None)   # corta la línea: alistamiento nuevo
                ys.append(None)
            xs.append(r["iteracion"])
            ys.append(len(r["herr_acum"][j]))
            lote_prev = r["lote"]
        ax.step(xs, ys, where="post", linewidth=2.4, color=PALETA[k % len(PALETA)],
                label=f"Máquina {j}  (máx. {mt.cap_herr})", zorder=4)
        ax.plot(xs, ys, "o", markersize=5.5, color=PALETA[k % len(PALETA)], zorder=5)
        ax.axhline(mt.cap_herr, color=PALETA[k % len(PALETA)], linestyle=":",
                   linewidth=1.4, alpha=0.8, zorder=3)

    ax.set_xticks(its)
    ax.set_ylim(0, cap_max + 1.2)
    ax.set_yticks(range(0, int(cap_max) + 2))
    ax.grid(True, axis="y", color="#e2e8f0", linestyle="--", alpha=0.9, zorder=2)
    ag_estilo(ax, "Gráfico 5 — Portaherramientas ocupados por iteración "
                  "(línea punteada = capacidad)",
              "Iteración de la heurística", "Espacios ocupados")
    ax.legend(fontsize=9, framealpha=0.95, facecolor="white", edgecolor="#e2e8f0", loc="lower right")
    fig.tight_layout()
    return fig


def ag_g6_mapa_herramientas(lotes, tipos):
    """Gráfico 6 — Qué herramienta está cargada en qué lote (alistamiento de cada lote)."""
    herr = []
    for j in tipos:
        for l in lotes:
            for h in l.tools[j]:
                if (j, h) not in herr:
                    herr.append((j, h))
    if not herr:
        fig, ax = plt.subplots(figsize=(11, 2.2), facecolor="white")
        ax.text(0.5, 0.5, "No se cargó ninguna herramienta.", ha="center", va="center",
                fontsize=11, color="#64748b")
        ax.axis("off")
        return fig

    fig, ax = plt.subplots(figsize=(11, max(2.4, 0.42 * len(herr) + 1.8)), facecolor="white")
    codigos = list(tipos.keys())
    for fi, (j, h) in enumerate(herr):
        y = len(herr) - 1 - fi
        color = PALETA[codigos.index(j) % len(PALETA)]
        for l in lotes:
            x = l.indice - 1
            cargada = h in l.tools[j]
            ax.broken_barh([(x + 0.08, 0.84)], (y - 0.34, 0.68),
                           facecolors=color if cargada else "white",
                           edgecolor=color if cargada else GRIS_BORDE,
                           linewidth=1.3, alpha=1.0 if cargada else 1.0, zorder=3)
            if cargada:
                ax.text(x + 0.5, y, "●", ha="center", va="center", color="white",
                        fontsize=11, zorder=4)
    ax.set_yticks(list(range(len(herr))))
    ax.set_yticklabels([f"{h}  (máq. {j})" for j, h in reversed(herr)],
                       fontsize=9.5, color=AG_AZUL)
    ax.set_xticks([l.indice - 0.5 for l in lotes])
    ax.set_xticklabels([f"Lote {l.indice}" for l in lotes], fontsize=10, color=AG_AZUL)
    ax.set_xlim(0, len(lotes))
    ax.set_ylim(-0.7, len(herr) - 0.3)
    ag_estilo(ax, "Gráfico 6 — Alistamiento: herramientas cargadas en cada lote")
    fig.tight_layout()
    return fig


# ──────────────────────────────────────────────────────────────
#  3. DESCARGAS
# ──────────────────────────────────────────────────────────────

def ag_excel(dfs, figs):
    """Excel con todas las hojas de datos y una hoja con los gráficos incrustados.
    Devuelve (bytes, motor) o (None, None) si no hay motor disponible."""
    motor = None
    for cand in ("xlsxwriter", "openpyxl"):
        try:
            __import__(cand)
            motor = cand
            break
        except ImportError:
            continue
    if motor is None:
        return None, None

    imgs = []
    for titulo, fig in figs.items():
        b = io.BytesIO()
        fig.savefig(b, format="png", dpi=120, bbox_inches="tight", facecolor="white")
        b.seek(0)
        imgs.append((titulo, b))

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine=motor) as w:
        for hoja, df in dfs.items():
            df.to_excel(w, sheet_name=hoja[:31], index=False)
        try:
            if motor == "xlsxwriter":
                ws = w.book.add_worksheet("Gráficos")
                fila = 0
                for titulo, b in imgs:
                    ws.write(fila, 0, titulo)
                    ws.insert_image(fila + 1, 0, f"{titulo}.png",
                                    {"image_data": b, "x_scale": 0.62, "y_scale": 0.62})
                    fila += 32
            else:
                from openpyxl.drawing.image import Image as XLImage
                ws = w.book.create_sheet("Gráficos")
                fila = 1
                for titulo, b in imgs:
                    ws.cell(row=fila, column=1, value=titulo)
                    img = XLImage(b)
                    img.width, img.height = img.width * 0.62, img.height * 0.62
                    ws.add_image(img, f"A{fila + 1}")
                    fila += 32
        except Exception:
            pass  # si falla la incrustación, el Excel de datos igual se entrega
    buf.seek(0)
    return buf.getvalue(), motor


def ag_pdf(figs, resumen, dfs):
    """Informe gráfico en PDF: portada con el resumen y una página por gráfico."""
    from matplotlib.backends.backend_pdf import PdfPages

    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        j_lim, rec_lim, v_lim, lote_lim = resumen["limitante"]
        portada, ax = plt.subplots(figsize=(11.69, 8.27), facecolor="white")
        ax.axis("off")
        ax.text(0.5, 0.93, "Análisis gráfico de lotes, máquinas e iteraciones",
                ha="center", fontsize=20, fontweight="bold", color=AG_AZUL)
        ax.text(0.5, 0.875, "FMS.lab — Heurística de Selección de Partes",
                ha="center", fontsize=12, color="#2563eb")
        ax.text(0.5, 0.845,
                datetime.datetime.now().strftime("Generado el %d/%m/%Y a las %H:%M"),
                ha="center", fontsize=9.5, color="#64748b")
        lineas = [
            ("Lotes formados", str(resumen["lotes"])),
            ("Tipos de máquina", str(resumen["tipos"])),
            ("Máquinas en el sistema", str(resumen["maquinas"])),
            ("Iteraciones de la heurística", str(resumen["iteraciones"])),
            ("Pedidos fraccionados", str(resumen["fraccionamientos"])),
            ("Unidades programadas", str(resumen["unidades"])),
            ("Utilización media de las máquinas", f"{resumen['util_media']:.2f} %"),
            ("Recurso limitante", f"{rec_lim} en la máquina {j_lim} "
                                  f"(Lote {lote_lim}, {v_lim:.2f} %)"),
        ]
        y = 0.74
        for etq, val in lineas:
            ax.text(0.16, y, etq, fontsize=11.5, color="#374151")
            ax.text(0.84, y, val, fontsize=11.5, fontweight="bold", color=AG_AZUL, ha="right")
            ax.plot([0.16, 0.84], [y - 0.018, y - 0.018], color="#e2e8f0", linewidth=0.8)
            y -= 0.055
        ax.text(0.5, 0.10,
                "La heurística de selección de partes es constructiva de una sola pasada: cada\n"
                "iteración agrega un pedido al lote abierto. El 'recurso limitante' es el que más\n"
                "se satura y el que obliga a cerrar el lote.",
                ha="center", fontsize=9.5, color="#64748b")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        pdf.savefig(portada, facecolor="white")
        plt.close(portada)

        for fig in figs.values():
            pdf.savefig(fig, facecolor="white", bbox_inches="tight")

        meta = pdf.infodict()
        meta["Title"] = "FMS.lab — Análisis gráfico de lotes, máquinas e iteraciones"
        meta["Author"] = "FMS.lab — UTP"
    buf.seek(0)
    return buf.getvalue()


# ──────────────────────────────────────────────────────────────
#  4. SECCIÓN DE LA INTERFAZ
# ──────────────────────────────────────────────────────────────

def seccion_analisis_grafico(lotes, bitacora, tipos):
    """Nueva sección al final de la página. No altera nada de lo existente."""
    if not lotes or not bitacora:
        return

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Análisis gráfico de lotes, máquinas '
                'e iteraciones</div>', unsafe_allow_html=True)

    colores = ag_colores(bitacora)
    df_lotes, df_maq, df_gantt, df_iter, df_rech = ag_tablas(lotes, bitacora, tipos)
    res = ag_resumen(lotes, bitacora, tipos)
    j_lim, rec_lim, v_lim, lote_lim = res["limitante"]

    # ---- Resumen general ----
    c = st.columns(5)
    tarjetas = [
        ("Lotes", res["lotes"], ""),
        ("Máquinas", res["maquinas"], f"{res['tipos']} tipo(s)"),
        ("Iteraciones", res["iteraciones"], f"{res['fraccionamientos']} fraccionamiento(s)"),
        ("Unidades programadas", res["unidades"], ""),
        ("Utilización media", f"{num(res['util_media'])} %", ""),
    ]
    for col, (etq, val, pie) in zip(c, tarjetas):
        col.markdown(
            f'<div class="metric-card"><div class="metric-label">{etq}</div>'
            f'<div class="metric-value">{val}</div>'
            + (f'<div style="font-size:0.78rem;color:#64748b;margin-top:4px;">{pie}</div>'
               if pie else "")
            + '</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="alert-warn">🎯 <b>Recurso limitante:</b> '
        f'<b>{rec_lim}</b> de la máquina <b>{j_lim}</b>, en el <b>Lote {lote_lim}</b>, '
        f'con {num(v_lim)} % de ocupación. Es el recurso que se satura primero y el que '
        f'obliga a cerrar el lote — el equivalente al cuello de botella en esta heurística.'
        f'</div>', unsafe_allow_html=True)

    st.markdown('<div class="alert-info">📌 Esta heurística es <b>constructiva de una sola '
                'pasada</b>: cada iteración agrega un pedido al lote abierto, no mejora una '
                'solución anterior. Por eso los gráficos muestran <b>cómo se fueron consumiendo '
                'los recursos</b> iteración a iteración, no una curva de optimización.</div>',
                unsafe_allow_html=True)

    # ---- Gráficos ----
    figs = {}
    figs["Gráfico 1 — Composición de los lotes"] = ag_g1_composicion(lotes, bitacora, colores)
    figs["Gráfico 2 — Gantt de máquinas"] = ag_g2_gantt(lotes, bitacora, tipos, colores)
    figs["Gráfico 3 — Cargas y recurso limitante"] = ag_g3_cargas(lotes, tipos)
    figs["Gráfico 4 — Evolución por iteración"] = ag_g4_evolucion(lotes, bitacora, tipos)
    figs["Gráfico 5 — Portaherramientas por iteración"] = ag_g5_portaherramientas(
        lotes, bitacora, tipos)
    figs["Gráfico 6 — Herramientas por lote"] = ag_g6_mapa_herramientas(lotes, tipos)

    pies = {
        "Gráfico 1 — Composición de los lotes":
            "Cada barra es un lote; cada segmento, un pedido con las unidades que se le "
            "programaron. La notación parte (asignadas/tamaño original) muestra los "
            "fraccionamientos.",
        "Gráfico 2 — Gantt de máquinas":
            "Eje X: la bolsa de tiempo del tipo de máquina (mⱼ × Pⱼ). Cada bloque es un pedido y "
            "su ancho es la duración. El área gris es la capacidad no utilizada.",
        "Gráfico 3 — Cargas y recurso limitante":
            "Ocupación de los dos recursos del modelo. La barra con borde rojo es el recurso que "
            "más se satura en ese lote.",
        "Gráfico 4 — Evolución por iteración":
            "Cómo creció el tiempo acumulado en cada tipo de máquina. Al abrir un lote nuevo "
            "todo vuelve a cero: es el alistamiento.",
        "Gráfico 5 — Portaherramientas por iteración":
            "Ocupación de los portaherramientas. Cuando la línea toca la punteada, ya no caben "
            "herramientas nuevas y solo entran pedidos que reutilicen las cargadas.",
        "Gráfico 6 — Herramientas por lote":
            "Alistamiento de cada lote: qué herramienta se cargó en cada uno y en qué máquina.",
    }
    for titulo, fig in figs.items():
        st.markdown(f"#### {titulo}")
        st.pyplot(fig, use_container_width=True)
        st.caption(pies.get(titulo, ""))

    # ---- Datos de respaldo ----
    with st.expander("📄 Datos que alimentan estos gráficos"):
        t = st.tabs(["Lotes", "Máquinas", "Asignaciones (Gantt)", "Iteraciones", "Rechazos"])
        for tab, df in zip(t, [df_lotes, df_maq, df_gantt, df_iter, df_rech]):
            with tab:
                if df.empty:
                    st.caption("Sin registros.")
                else:
                    st.dataframe(df, hide_index=True, use_container_width=True)

    # ---- Descargas ----
    st.markdown("#### Descargar el análisis")
    dfs = {"Resumen": pd.DataFrame([{
        "Lotes": res["lotes"], "Tipos de máquina": res["tipos"],
        "Máquinas": res["maquinas"], "Iteraciones": res["iteraciones"],
        "Fraccionamientos": res["fraccionamientos"], "Unidades": res["unidades"],
        "Utilización media (%)": round(res["util_media"], 2),
        "Recurso limitante": f"{rec_lim} en {j_lim} (Lote {lote_lim}, {round(v_lim, 2)} %)",
    }]),
        "Lotes": df_lotes, "Maquinas": df_maq, "Asignaciones": df_gantt,
        "Iteraciones": df_iter, "Rechazos": df_rech,
    }

    ts_ag = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    c1, c2 = st.columns(2)
    with c1:
        datos_xlsx, motor = ag_excel(dfs, figs)
        if datos_xlsx:
            st.download_button("⬇️ Descargar análisis en Excel", datos_xlsx,
                               f"fms_analisis_grafico_{ts_ag}.xlsx",
                               "application/vnd.openxmlformats-officedocument."
                               "spreadsheetml.sheet",
                               use_container_width=True, key="ag_dl_xlsx")
        else:
            st.markdown('<div class="alert-warn">Para el Excel agrega <code>xlsxwriter</code> '
                        'a requirements.txt.</div>', unsafe_allow_html=True)
    with c2:
        try:
            datos_pdf = ag_pdf(figs, res, dfs)
            st.download_button("⬇️ Descargar análisis en PDF", datos_pdf,
                               f"fms_analisis_grafico_{ts_ag}.pdf", "application/pdf",
                               use_container_width=True, key="ag_dl_pdf")
        except Exception as e:
            st.markdown(f'<div class="alert-warn">No se pudo generar el PDF: {e}</div>',
                        unsafe_allow_html=True)

    for fig in figs.values():
        plt.close(fig)

# ══════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    if "cfg" not in st.session_state:
        st.session_state["cfg"] = caso_articulo()          # arranca con el caso del artículo
    if "resultado" not in st.session_state:
        st.session_state["resultado"] = None

    # Ejecución automática al abrir: demuestra que reproduce el artículo
    if st.session_state["resultado"] is None and not st.session_state.get("_intento_inicial"):
        st.session_state["_intento_inicial"] = True
        try:
            tipos, pedidos = cfg_a_objetos(st.session_state["cfg"])
            if not validar(tipos, pedidos)[0]:
                lotes, bitacora = ejecutar(pedidos, tipos)
                st.session_state["resultado"] = {"lotes": lotes, "bitacora": bitacora,
                                                 "tipos": tipos}
        except Exception:
            pass

    mostrar_header()
    mod = sidebar_nav()

    if "Marco" in mod:
        modulo_teoria()
    elif "Configurar" in mod:
        modulo_configurar()
    elif "Ejecutar" in mod:
        modulo_ejecutar()
    elif "Resultados" in mod:
        modulo_resultados()
    elif "Reportes" in mod:
        modulo_reportes()
    elif "Referencias" in mod:
        modulo_referencias()


if __name__ == "__main__":
    main()
