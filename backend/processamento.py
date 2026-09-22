from backend.validacao import validar_mrna
from backend.traducao import traduzir
from backend.modelos import ResultadoProcessamento

# PROCESSAMENTO DE UM ÚNICO mRNA

def processar_mrna(mrna, numero_linha):
    """Valida e, se possível, traduz uma sequência de mRNA."""

    resultado_validacao = validar_mrna(mrna)

    # Se houve algum erro na validação, não existe tradução.
    if resultado_validacao["status"] == "ERRO":
        return ResultadoProcessamento(
            linha=numero_linha,
            status="ERRO",
            resultado=resultado_validacao["resultado"],
            proteina=None
        )

    # Se chegou aqui, o mRNA é válido.
    sequencia_codificante = resultado_validacao["sequencia_codificante"]

    proteina = traduzir(sequencia_codificante)

    return ResultadoProcessamento(
        linha=numero_linha,
        status="OK",
        resultado="CORRETO",
        proteina=proteina,

        cap="OK",
        start=f'{resultado_validacao["start"]} - OK',
        quadro_leitura="OK",
        stop=f'{resultado_validacao["stop"]} - OK',
        cauda_poli_a="100 A - OK",
        traducao="OK"
    )

def processar_arquivo(caminho_entrada):
    """Processa todos os mRNAs presentes no arquivo."""

    resultados = []

    with open(caminho_entrada, "r", encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):

            mrna = linha.strip()

            resultado = processar_mrna(
                mrna,
                numero_linha
            )

            resultados.append(resultado)

    return resultados

def salvar_resultados(resultados, caminho_saida):
    """Salva os resultados no formato exigido pela especificação."""

    with open(caminho_saida, "w", encoding="utf-8") as arquivo:

        arquivo.write("linha;status;resultado;proteina\n")

        for resultado in resultados:

            if resultado.proteina is None:
                proteina = "NÃO GERADA"
            else:
                proteina = resultado.proteina

            arquivo.write(
                f"{resultado.linha};"
                f"{resultado.status};"
                f"{resultado.resultado};"
                f"{proteina}\n"
            )