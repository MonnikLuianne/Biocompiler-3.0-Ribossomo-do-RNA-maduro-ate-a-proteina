from backend.processamento import processar_arquivo, salvar_resultados


def main():
    caminho_entrada = "dados/entradas_vindas_do_biocompiler_2.0.txt"
    caminho_saida = "dados/resultados.txt"

    resultados = processar_arquivo(caminho_entrada)

    print("=" * 40)
    print("RIBOSSOMO - PROTEIN TRANSLATOR")
    print("=" * 40)

    for resultado in resultados:

        print(f"ENTRADA: {resultado.linha}")

        if resultado.status == "OK":
            print("STATUS: CORRETO")
            print(f"CAP 5': {resultado.cap}")
            print(f"START: {resultado.start}")
            print(f"Quadro de leitura: {resultado.quadro_leitura}")
            print(f"STOP: {resultado.stop}")
            print(f"Cauda poli-A: {resultado.cauda_poli_a}")
            print(f"Tradução: {resultado.traducao}")
            print(f"PROTEÍNA: {resultado.proteina}")

        else:
            print("STATUS: ERRO")
            print(f"TIPO: {resultado.resultado}")
            print("PROTEÍNA: NÃO GERADA")

        print("-" * 40)

    salvar_resultados(resultados, caminho_saida)

    print(f"Resultados salvos em: {caminho_saida}")


if __name__ == "__main__":
    main()