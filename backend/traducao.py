CODONS_STOP = {"UAA", "UAG", "UGA"}

CODIGO_GENETICO = {
    "UUU": "Phe", "UUC": "Phe",
    "UUA": "Leu", "UUG": "Leu",

    "UCU": "Ser", "UCC": "Ser",
    "UCA": "Ser", "UCG": "Ser",

    "UAU": "Tyr", "UAC": "Tyr",

    "UGU": "Cys", "UGC": "Cys",
    "UGG": "Trp",

    "CUU": "Leu", "CUC": "Leu",
    "CUA": "Leu", "CUG": "Leu",

    "CCU": "Pro", "CCC": "Pro",
    "CCA": "Pro", "CCG": "Pro",

    "CAU": "His", "CAC": "His",
    "CAA": "Gln", "CAG": "Gln",

    "CGU": "Arg", "CGC": "Arg",
    "CGA": "Arg", "CGG": "Arg",

    "AUU": "Ile", "AUC": "Ile",
    "AUA": "Ile",
    "AUG": "Met",

    "ACU": "Thr", "ACC": "Thr",
    "ACA": "Thr", "ACG": "Thr",

    "AAU": "Asn", "AAC": "Asn",
    "AAA": "Lys", "AAG": "Lys",

    "AGU": "Ser", "AGC": "Ser",
    "AGA": "Arg", "AGG": "Arg",

    "GUU": "Val", "GUC": "Val",
    "GUA": "Val", "GUG": "Val",

    "GCU": "Ala", "GCC": "Ala",
    "GCA": "Ala", "GCG": "Ala",

    "GAU": "Asp", "GAC": "Asp",
    "GAA": "Glu", "GAG": "Glu",

    "GGU": "Gly", "GGC": "Gly",
    "GGA": "Gly", "GGG": "Gly",
}

def traduzir(sequencia_codificante):
    aminoacidos = []

    for posicao in range(0, len(sequencia_codificante), 3):
        codon = sequencia_codificante[posicao:posicao + 3]

        if codon in CODONS_STOP:
            break

        aminoacido = CODIGO_GENETICO[codon]

        aminoacidos.append(aminoacido)

    return "-".join(aminoacidos)