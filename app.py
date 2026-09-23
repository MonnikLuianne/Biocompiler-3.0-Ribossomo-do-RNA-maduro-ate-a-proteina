import base64
import csv
import html
import io
import os
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

from backend.processamento import processar_mrna
from backend.validacao import validar_mrna


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="BioCompiler 3.0 | Ribossomo",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
FUNDO = BASE_DIR / "plano-de-fundo-do-dia-nacional-da-ciencia_23-2149283127.avif"
ARQUIVO_RIBOSSOMO = BASE_DIR / "dados" / "entrada_ribossomo.txt"
ARQUIVO_BIOCOMPILER_2 = BASE_DIR / "dados" / "entradas_vindas_do_biocompiler_2.0.txt"


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================


def carregar_fundo() -> str | None:
    """Retorna a imagem de fundo em base64, quando disponível."""

    if not FUNDO.exists():
        return None

    with open(FUNDO, "rb") as arquivo:
        return base64.b64encode(arquivo.read()).decode("utf-8")


@st.cache_data(show_spinner=False)
def interpretar_arquivo(conteudo: bytes) -> tuple[list[str], str, int]:
    """
    Lê tanto o formato oficial do Ribossomo (um mRNA por linha)
    quanto a saída exportada pelo BioCompiler 2.0.

    Retorna:
        mrnas: sequências que serão processadas;
        formato: descrição da origem detectada;
        descartadas: linhas do BioCompiler 2.0 que não geraram mRNA maduro.
    """

    texto = conteudo.decode("utf-8-sig").strip()

    if not texto:
        return [], "Arquivo vazio", 0

    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]

    # Saída do BioCompiler 2.0: linha;status;resultado;mRNA_maduro
    if linhas and "mRNA_maduro" in linhas[0] and ";" in linhas[0]:
        leitor = csv.DictReader(io.StringIO(texto), delimiter=";")
        mrnas = []
        descartadas = 0

        campos = set(leitor.fieldnames or [])
        obrigatorios = {"status", "mRNA_maduro"}

        if not obrigatorios.issubset(campos):
            raise ValueError(
                "O arquivo possui cabeçalho, mas não contém as colunas "
                "'status' e 'mRNA_maduro'."
            )

        for registro in leitor:
            status = (registro.get("status") or "").strip()
            mrna = (registro.get("mRNA_maduro") or "").strip()

            if status == "OK" and mrna and mrna != "NÃO GERADO":
                mrnas.append(mrna)
            else:
                descartadas += 1

        return mrnas, "Saída do BioCompiler 2.0", descartadas

    # Formato oficial do Ribossomo: um mRNA maduro por linha.
    return linhas, "mRNA maduro por linha", 0


def carregar_arquivo_padrao() -> tuple[list[str], str, int, str]:
    """Carrega automaticamente o melhor arquivo disponível no projeto."""

    if ARQUIVO_RIBOSSOMO.exists():
        with open(ARQUIVO_RIBOSSOMO, "rb") as arquivo:
            mrnas, formato, descartadas = interpretar_arquivo(arquivo.read())
        return mrnas, formato, descartadas, ARQUIVO_RIBOSSOMO.name

    if ARQUIVO_BIOCOMPILER_2.exists():
        with open(ARQUIVO_BIOCOMPILER_2, "rb") as arquivo:
            mrnas, formato, descartadas = interpretar_arquivo(arquivo.read())
        return mrnas, formato, descartadas, ARQUIVO_BIOCOMPILER_2.name

    return [], "Nenhum arquivo", 0, "—"


def gerar_arquivo_exportacao(resultados: list[dict]) -> str:
    """Gera o TXT no padrão solicitado para correção automática."""

    linhas = ["linha;status;resultado;proteina"]

    for item in resultados:
        proteina = item["Proteína"] if item["Proteína"] else "NÃO GERADA"
        linhas.append(
            f"{item['Entrada']};"
            f"{item['Status exportação']};"
            f"{item['Resultado']};"
            f"{proteina}"
        )

    return "\n".join(linhas)


def resumo_validacoes(mrna: str, resultado: str) -> list[tuple[str, str]]:
    """Monta um resumo visual das etapas já validadas para uma entrada."""

    ordem = [
        "CAP 5'",
        "Cauda poli-A",
        "Bases A/U/G/C",
        "START (AUG)",
        "Quadro de leitura",
        "STOP em fase",
        "Tradução",
    ]

    erro_para_etapa = {
        "BUG - CAP 5'": "CAP 5'",
        "BUG - cauda poli-A": "Cauda poli-A",
        "BUG - sequência RNA inválida": "Bases A/U/G/C",
        "BUG - START ausente": "START (AUG)",
        "BUG - quadro de leitura": "Quadro de leitura",
        "BUG - STOP ausente": "STOP em fase",
    }

    if resultado == "CORRETO":
        return [(etapa, "OK") for etapa in ordem]

    etapa_erro = erro_para_etapa.get(resultado)
    if etapa_erro is None:
        return [(etapa, "—") for etapa in ordem]

    indice_erro = ordem.index(etapa_erro)
    resumo = []

    for indice, etapa in enumerate(ordem):
        if indice < indice_erro:
            resumo.append((etapa, "OK"))
        elif indice == indice_erro:
            resumo.append((etapa, "ERRO"))
        else:
            resumo.append((etapa, "—"))

    return resumo


def badge(texto: str, tipo: str = "neutral") -> str:
    classe = {
        "ok": "badge-ok",
        "erro": "badge-error",
        "info": "badge-info",
        "neutral": "badge-neutral",
    }.get(tipo, "badge-neutral")

    return f'<span class="status-badge {classe}">{html.escape(texto)}</span>'


def formatar_mrna(mrna: str, resultado_validacao: dict) -> str:
    """Destaca visualmente CAP, START, STOP e cauda poli-A quando identificáveis."""

    sequencia = html.escape(mrna)

    if sequencia.startswith("m7Gppp"):
        sequencia = (
            '<span class="seq-cap">m7Gppp</span>'
            + sequencia[len("m7Gppp") :]
        )

    if len(mrna) >= 100 and mrna.endswith("A" * 100):
        prefixo = sequencia[:-100]
        cauda = sequencia[-100:]
        sequencia = prefixo + f'<span class="seq-tail">{cauda}</span>'

    # Destacamos START/STOP somente quando a validação os identificou de forma inequívoca.
    if resultado_validacao.get("status") == "OK":
        inicio = resultado_validacao.get("inicio")
        fim = resultado_validacao.get("fim")

        # Os índices acima não contam a CAP; aqui operamos na sequência sem marcações HTML.
        corpo = html.escape(mrna)
        deslocamento = len("m7Gppp") if mrna.startswith("m7Gppp") else 0
        inicio_abs = deslocamento + inicio
        fim_abs = deslocamento + fim

        partes = [
            html.escape(mrna[:inicio_abs]),
            f'<span class="seq-start">{html.escape(mrna[inicio_abs:inicio_abs + 3])}</span>',
            html.escape(mrna[inicio_abs + 3:fim_abs]),
            f'<span class="seq-stop">{html.escape(mrna[fim_abs:fim_abs + 3])}</span>',
            html.escape(mrna[fim_abs + 3:]),
        ]
        corpo = "".join(partes)

        if corpo.startswith("m7Gppp"):
            corpo = '<span class="seq-cap">m7Gppp</span>' + corpo[len("m7Gppp") :]

        if mrna.endswith("A" * 100):
            indice_cauda = corpo.rfind("A" * 100)
            if indice_cauda != -1:
                corpo = (
                    corpo[:indice_cauda]
                    + f'<span class="seq-tail">{corpo[indice_cauda:]}</span>'
                )

        return corpo

    return sequencia


# ============================================================
# ESTILO / FUNDO
# ============================================================

imagem_base64 = carregar_fundo()

fundo_css = ""
if imagem_base64:
    fundo_css = f"""
    background-image:
        linear-gradient(rgba(255, 247, 241, 0.63), rgba(255, 247, 241, 0.63)),
        url("data:image/avif;base64,{imagem_base64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    """

st.markdown(
    f"""
    <style>
    :root {{
        --ink: #18243d;
        --muted: #5f6878;
        --surface: rgba(255,255,255,0.88);
        --surface-strong: rgba(255,255,255,0.96);
        --border: rgba(24,36,61,0.12);
        --accent: #1f6f78;
        --accent-2: #d97a3a;
        --success: #26734d;
        --danger: #b64141;
        --shadow: 0 16px 40px rgba(48, 35, 31, 0.12);
    }}

    .stApp {{
        {fundo_css}
        color: var(--ink);
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stToolbar"] {{
        right: 0.8rem;
    }}

    .block-container {{
        max-width: 1320px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }}

    h1, h2, h3, h4, p, label, li, span {{
        color: var(--ink);
    }}

    h1 {{
        font-weight: 800 !important;
        letter-spacing: -0.03em;
    }}

    h2, h3 {{
        letter-spacing: -0.015em;
    }}

    .hero {{
        background: linear-gradient(135deg, rgba(255,255,255,0.97), rgba(255,250,246,0.90));
        border: 1px solid var(--border);
        border-radius: 26px;
        padding: 1.8rem 2rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.25rem;
        backdrop-filter: blur(12px);
    }}

    .hero-eyebrow {{
        display: inline-block;
        padding: 0.35rem 0.65rem;
        border-radius: 999px;
        background: rgba(31,111,120,0.10);
        color: var(--accent) !important;
        font-size: 0.80rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }}

    .hero-title {{
        font-size: clamp(2rem, 5vw, 3.5rem);
        line-height: 1.05;
        font-weight: 850;
        margin: 0;
        color: var(--ink) !important;
    }}

    .hero-subtitle {{
        margin-top: 0.75rem;
        margin-bottom: 0;
        color: var(--muted) !important;
        font-size: 1.05rem;
        max-width: 840px;
    }}

    .pipeline {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        align-items: center;
        margin-top: 1.2rem;
    }}

    .pipeline-step {{
        padding: 0.45rem 0.72rem;
        border-radius: 12px;
        background: rgba(24,36,61,0.06);
        border: 1px solid rgba(24,36,61,0.08);
        font-weight: 700;
        font-size: 0.84rem;
    }}

    .pipeline-arrow {{
        color: var(--accent-2) !important;
        font-weight: 900;
    }}

    div[data-testid="stMetric"] {{
        background: var(--surface-strong);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1rem 1.15rem;
        box-shadow: 0 8px 24px rgba(48,35,31,0.08);
    }}

    div[data-testid="stMetricLabel"] p {{
        color: var(--muted) !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: var(--ink) !important;
        font-weight: 800 !important;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--surface);
        border: 1px solid var(--border) !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(48,35,31,0.08);
        backdrop-filter: blur(12px);
    }}

    div[data-testid="stExpander"] {{
        background: var(--surface-strong) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 22px rgba(48,35,31,0.07);
        overflow: hidden;
    }}

    div[data-testid="stExpander"] summary {{
        color: var(--ink) !important;
        font-weight: 750 !important;
    }}

    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] div {{
        color: var(--ink);
    }}

    .status-badge {{
        display: inline-block;
        border-radius: 999px;
        padding: 0.25rem 0.58rem;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.02em;
        margin-right: 0.3rem;
    }}

    .badge-ok {{ background: rgba(38,115,77,0.12); color: #1f6844 !important; }}
    .badge-error {{ background: rgba(182,65,65,0.12); color: #9f3434 !important; }}
    .badge-info {{ background: rgba(31,111,120,0.12); color: #185e66 !important; }}
    .badge-neutral {{ background: rgba(24,36,61,0.08); color: #4f596a !important; }}

    .sequence-box {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        background: #f8fafb;
        border: 1px solid rgba(24,36,61,0.10);
        border-radius: 14px;
        padding: 0.85rem 1rem;
        overflow-wrap: anywhere;
        line-height: 1.75;
        font-size: 0.88rem;
        margin: 0.45rem 0 0.9rem 0;
    }}

    .seq-cap {{ color: #7048a8 !important; font-weight: 900; }}
    .seq-start {{ color: #17814b !important; font-weight: 900; background: rgba(23,129,75,0.10); border-radius: 4px; padding: 1px 3px; }}
    .seq-stop {{ color: #bd3f3f !important; font-weight: 900; background: rgba(189,63,63,0.10); border-radius: 4px; padding: 1px 3px; }}
    .seq-tail {{ color: #ad6a18 !important; font-weight: 750; }}

    .protein-box {{
        background: linear-gradient(135deg, rgba(31,111,120,0.10), rgba(38,115,77,0.08));
        border: 1px solid rgba(31,111,120,0.18);
        border-radius: 14px;
        padding: 0.8rem 1rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-weight: 800;
        overflow-wrap: anywhere;
    }}

    .small-note {{
        color: var(--muted) !important;
        font-size: 0.86rem;
    }}

    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #1f6f78, #2e8582) !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 22px rgba(31,111,120,0.20);
    }}

    .stDownloadButton > button {{
        border-radius: 14px !important;
        border: 1px solid rgba(31,111,120,0.25) !important;
        font-weight: 750 !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        background: rgba(255,255,255,0.78) !important;
        border: 1px dashed rgba(31,111,120,0.35) !important;
        border-radius: 16px !important;
    }}

    [data-testid="stDataFrame"] {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid var(--border);
    }}

    hr {{
        border-color: rgba(24,36,61,0.12) !important;
    }}

    @media (max-width: 700px) {{
        .block-container {{ padding-top: 1.2rem; }}
        .hero {{ padding: 1.35rem; border-radius: 20px; }}
        .pipeline-arrow {{ display: none; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">BioCompiler 3.0 · Fase III</div>
        <div class="hero-title">🧬 Ribossomo — Protein Translator</div>
        <p class="hero-subtitle">
            Simulação didática da tradução de <strong>mRNA maduro</strong> em uma
            sequência de aminoácidos, com validação de CAP 5', START, quadro de
            leitura, STOP e cauda poli-A.
        </p>
        <div class="pipeline">
            <span class="pipeline-step">mRNA maduro</span>
            <span class="pipeline-arrow">→</span>
            <span class="pipeline-step">Validar estrutura</span>
            <span class="pipeline-arrow">→</span>
            <span class="pipeline-step">Localizar AUG</span>
            <span class="pipeline-arrow">→</span>
            <span class="pipeline-step">Ler códons</span>
            <span class="pipeline-arrow">→</span>
            <span class="pipeline-step">STOP em fase</span>
            <span class="pipeline-arrow">→</span>
            <span class="pipeline-step">Proteína</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ENTRADA
# ============================================================

with st.container(border=True):
    st.subheader("📂 Entrada")
    st.caption(
        "Use um TXT com um mRNA maduro por linha. Para integração entre as etapas, "
        "o front também reconhece diretamente a saída exportada pelo BioCompiler 2.0."
    )

    arquivo_upload = st.file_uploader(
        "Selecionar arquivo",
        type=["txt", "csv"],
        help="Formato oficial: uma sequência de mRNA maduro por linha.",
    )

    try:
        if arquivo_upload is not None:
            entradas, formato_detectado, descartadas, nome_arquivo = (
                *interpretar_arquivo(arquivo_upload.getvalue()),
                arquivo_upload.name,
            )
        else:
            entradas, formato_detectado, descartadas, nome_arquivo = carregar_arquivo_padrao()
    except Exception as erro:
        st.error(f"Não foi possível interpretar o arquivo: {erro}")
        entradas, formato_detectado, descartadas, nome_arquivo = [], "Erro", 0, "—"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("mRNAs preparados", len(entradas))
    with col2:
        st.metric("Formato", "TXT")
    with col3:
        st.metric("Origem detectada", formato_detectado)
    with col4:
        st.metric("Descartados na conversão", descartadas)

    st.markdown(
        f'<p class="small-note">Arquivo ativo: <strong>{html.escape(nome_arquivo)}</strong></p>',
        unsafe_allow_html=True,
    )


# ============================================================
# EXECUÇÃO
# ============================================================

with st.container(border=True):
    st.subheader("▶ Execução")

    executar = st.button(
        "▶ Traduzir mRNAs",
        type="primary",
        use_container_width=True,
        disabled=not entradas,
    )

    if executar:
        resultados = []
        barra = st.progress(0, text="Preparando tradução...")

        for numero, mrna in enumerate(entradas, start=1):
            resultado_obj = processar_mrna(mrna, numero)
            validacao = validar_mrna(mrna)

            resultados.append(
                {
                    "Entrada": numero,
                    "mRNA": mrna,
                    "Status": "CORRETO" if resultado_obj.status == "OK" else "ERRO",
                    "Status exportação": resultado_obj.status,
                    "Resultado": resultado_obj.resultado,
                    "Proteína": resultado_obj.proteina,
                    "CAP 5'": resultado_obj.cap,
                    "START": resultado_obj.start,
                    "Quadro": resultado_obj.quadro_leitura,
                    "STOP": resultado_obj.stop,
                    "Cauda poli-A": resultado_obj.cauda_poli_a,
                    "Tradução": resultado_obj.traducao,
                    "Validação": validacao,
                }
            )

            barra.progress(
                numero / len(entradas),
                text=f"Processando entrada {numero} de {len(entradas)}...",
            )

        barra.empty()
        st.session_state["resultados_ribossomo"] = resultados
        st.success(f"Execução concluída: {len(resultados)} entrada(s) processada(s).")


# ============================================================
# RESULTADOS
# ============================================================

resultados = st.session_state.get("resultados_ribossomo", [])

if resultados:
    st.markdown("---")
    st.subheader("📋 Resultados")

    corretos = sum(1 for item in resultados if item["Resultado"] == "CORRETO")
    erros = len(resultados) - corretos
    taxa = (corretos / len(resultados) * 100) if resultados else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total", len(resultados))
    with c2:
        st.metric("Proteínas geradas", corretos)
    with c3:
        st.metric("Erros", erros)
    with c4:
        st.metric("Taxa de sucesso", f"{taxa:.1f}%")

    tabela = pd.DataFrame(
        [
            {
                "Entrada": item["Entrada"],
                "Status": item["Status"],
                "Resultado": item["Resultado"],
                "Proteína": item["Proteína"] or "NÃO GERADA",
            }
            for item in resultados
        ]
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Entrada": st.column_config.NumberColumn("Entrada", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Resultado": st.column_config.TextColumn("Diagnóstico", width="medium"),
            "Proteína": st.column_config.TextColumn("Proteína", width="large"),
        },
    )

    # ========================================================
    # DETALHAMENTO
    # ========================================================

    st.markdown("---")
    st.subheader("🔬 Detalhamento molecular")
    st.caption(
        "CAP 5' em roxo · START em verde · STOP em vermelho · cauda poli-A em laranja."
    )

    for item in resultados:
        icone = "✅" if item["Resultado"] == "CORRETO" else "⚠️"

        with st.expander(
            f"{icone} Entrada {item['Entrada']} — {item['Resultado']}",
            expanded=False,
        ):
            tipo_badge = "ok" if item["Resultado"] == "CORRETO" else "erro"
            st.markdown(
                badge(item["Resultado"], tipo_badge),
                unsafe_allow_html=True,
            )

            st.markdown("**mRNA maduro**")
            st.markdown(
                f'<div class="sequence-box">{formatar_mrna(item["mRNA"], item["Validação"])}</div>',
                unsafe_allow_html=True,
            )

            etapas = resumo_validacoes(item["mRNA"], item["Resultado"])
            badges_etapas = []
            for etapa, estado in etapas:
                if estado == "OK":
                    badges_etapas.append(badge(f"{etapa}: OK", "ok"))
                elif estado == "ERRO":
                    badges_etapas.append(badge(f"{etapa}: ERRO", "erro"))
                else:
                    badges_etapas.append(badge(f"{etapa}: —", "neutral"))

            st.markdown(" ".join(badges_etapas), unsafe_allow_html=True)

            if item["Resultado"] == "CORRETO":
                validacao = item["Validação"]
                st.markdown(
                    f"**Região codificante:** `{validacao['sequencia_codificante']}`"
                )
                st.markdown(
                    f'<div class="protein-box">PROTEÍNA · {html.escape(item["Proteína"])}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info(
                    "A proteína não foi gerada porque a entrada falhou em uma etapa "
                    "necessária antes da tradução completa."
                )

    # ========================================================
    # RELATÓRIO DIAGNÓSTICO
    # ========================================================

    st.markdown("---")
    st.subheader("📊 Relatório diagnóstico")

    contagem = Counter(item["Resultado"] for item in resultados)
    diagnostico_df = pd.DataFrame(
        {
            "Diagnóstico": list(contagem.keys()),
            "Quantidade": list(contagem.values()),
        }
    ).sort_values("Quantidade", ascending=False)

    st.dataframe(
        diagnostico_df,
        use_container_width=True,
        hide_index=True,
    )

    # ========================================================
    # EXPORTAÇÃO
    # ========================================================

    st.markdown("---")
    st.subheader("📥 Exportação")
    st.caption(
        "O arquivo segue o padrão: linha;status;resultado;proteina"
    )

    arquivo_saida = gerar_arquivo_exportacao(resultados)

    st.download_button(
        "📥 Baixar resultados.txt",
        data=arquivo_saida.encode("utf-8"),
        file_name="resultados.txt",
        mime="text/plain; charset=utf-8",
        use_container_width=True,
    )

else:
    st.info(
        "Carregue ou utilize o arquivo padrão do projeto e clique em "
        "**Traduzir mRNAs** para gerar os resultados."
    )
