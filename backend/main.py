from backend.conversao import converter_entrada
from backend.processamento import processar_arquivo, salvar_resultados


def main():

    # Arquivo bruto vindo do BioCompiler 2.0
    caminho_origem = (
        "dados/entradas_vindas_do_biocompiler_2.0.txt"
    )

    # Arquivo convertido para o formato exigido pelo Ribossomo
    caminho_entrada = (
        "dados/entrada_ribossomo.txt"
    )

    # Resultado final
    caminho_saida = (
        "dados/resultados.txt"
    )

    # ========================================================
    # 1. CONVERTER SAÍDA DO BIOCOMPILER 2.0
    # ========================================================

    quantidade = converter_entrada(
        caminho_origem,
        caminho_entrada
    )

    print(
        f"Conversão concluída: "
        f"{quantidade} mRNA(s) preparado(s)."
    )

    print()

    # ========================================================
    # 2. PROCESSAR OS mRNAs
    # ========================================================

    resultados = processar_arquivo(
        caminho_entrada
    )

    # ========================================================
    # 3. EXIBIR RESULTADOS NA TELA
    # ========================================================

    print("=" * 40)
    print("RIBOSSOMO - PROTEIN TRANSLATOR")
    print("=" * 40)

    for resultado in resultados:

        print(
            f"ENTRADA: {resultado.linha}"
        )

        if resultado.status == "OK":

            print("STATUS: CORRETO")

            print(
                f"CAP 5': "
                f"{resultado.cap}"
            )

            print(
                f"START: "
                f"{resultado.start}"
            )

            print(
                f"Quadro de leitura: "
                f"{resultado.quadro_leitura}"
            )

            print(
                f"STOP: "
                f"{resultado.stop}"
            )

            print(
                f"Cauda poli-A: "
                f"{resultado.cauda_poli_a}"
            )

            print(
                f"Tradução: "
                f"{resultado.traducao}"
            )

            print(
                f"PROTEÍNA: "
                f"{resultado.proteina}"
            )

        else:

            print("STATUS: ERRO")

            print(
                f"TIPO: "
                f"{resultado.resultado}"
            )

            print(
                "PROTEÍNA: NÃO GERADA"
            )

        print("-" * 40)

    # ========================================================
    # 4. SALVAR RESULTADOS
    # ========================================================

    salvar_resultados(
        resultados,
        caminho_saida
    )

    print(
        f"Resultados salvos em: "
        f"{caminho_saida}"
    )


if __name__ == "__main__":
    main()