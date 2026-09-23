import csv


def converter_entrada(caminho_origem, caminho_destino):
    """
    Converte a saída do BioCompiler 2.0 para o formato
    de entrada esperado pelo Ribossomo.
    """

    quantidade = 0

    with open(
        caminho_origem,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as origem, open(
        caminho_destino,
        "w",
        encoding="utf-8",
        newline=""
    ) as destino:

        leitor = csv.DictReader(
            origem,
            delimiter=";"
        )

        campos_obrigatorios = {
            "status",
            "mRNA_maduro"
        }

        if (
            not leitor.fieldnames
            or not campos_obrigatorios.issubset(leitor.fieldnames)
        ):
            raise ValueError(
                "Arquivo do BioCompiler 2.0 inválido: "
                "as colunas 'status' e 'mRNA_maduro' são obrigatórias."
            )

        for linha in leitor:

            status = (
                linha.get("status") or ""
            ).strip()

            mrna = (
                linha.get("mRNA_maduro") or ""
            ).strip()

            if (
                status == "OK"
                and mrna
                and mrna != "NÃO GERADO"
            ):
                destino.write(mrna + "\n")
                quantidade += 1

    return quantidade