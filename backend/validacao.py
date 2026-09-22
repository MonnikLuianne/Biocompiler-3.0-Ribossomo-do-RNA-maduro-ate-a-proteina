CAP_5 = "m7Gppp"
TAMANHO_CAUDA_POLI_A = 100
BASES_RNA = {"A", "U", "G", "C"}
CODONS_STOP = {"UAA", "UAG", "UGA"}


# ============================================================
# VALIDAÇÃO DA CAP 5'
# ============================================================

def validar_cap(mrna):
    """Verifica se o mRNA começa exatamente com m7Gppp."""
    return mrna.startswith(CAP_5)


# ============================================================
# VALIDAÇÃO DA CAUDA POLI-A
# ============================================================

def validar_cauda_poli_a(mrna):
    """Verifica se o mRNA termina com exatamente 100 adeninas consecutivas."""

    quantidade_a_finais = len(mrna) - len(mrna.rstrip("A"))

    return quantidade_a_finais == TAMANHO_CAUDA_POLI_A


# ============================================================
# SEPARAÇÃO DA CAP
# ============================================================

def remover_cap(mrna):
    """Remove a CAP 5' do mRNA."""

    return mrna[len(CAP_5):]


# ============================================================
# SEPARAÇÃO DA CAUDA POLI-A
# ============================================================

def remover_cauda_poli_a(sequencia):
    """Remove os 100 A da cauda poli-A."""

    return sequencia[:-TAMANHO_CAUDA_POLI_A]


# ============================================================
# VALIDAÇÃO DAS BASES DO RNA
# ============================================================

def validar_bases_rna(sequencia):
    """Verifica se a sequência contém somente A, U, G e C."""

    return all(base in BASES_RNA for base in sequencia)


# ============================================================
# LOCALIZAÇÃO DO START
# ============================================================

def encontrar_start(sequencia):
    """Localiza o primeiro códon AUG."""

    return sequencia.find("AUG")


# ============================================================
# LOCALIZAÇÃO DO STOP EM FASE
# ============================================================

def encontrar_stop_em_fase(sequencia, inicio):
    """
    Procura o primeiro códon STOP no mesmo quadro de leitura
    iniciado pelo AUG.
    """

    for posicao in range(inicio, len(sequencia) - 2, 3):

        codon = sequencia[posicao:posicao + 3]

        if codon in CODONS_STOP:
            return posicao, codon

    return -1, None


# ============================================================
# VERIFICAÇÃO DE STOP FORA DE FASE
# ============================================================

def existe_stop_fora_de_fase(sequencia, inicio):
    """
    Procura um STOP deslocado do quadro de leitura.

    A busca começa depois dos três primeiros códons da região
    iniciada pelo AUG para evitar interpretar combinações
    sobrepostas iniciais como um STOP funcional deslocado.
    """

    inicio_busca = inicio + 9

    for posicao in range(inicio_busca, len(sequencia) - 2):

        # Se estiver no quadro correto, não é STOP fora de fase.
        if (posicao - inicio) % 3 == 0:
            continue

        codon = sequencia[posicao:posicao + 3]

        if codon in CODONS_STOP:
            return True

    return False


# ============================================================
# VALIDAÇÃO DO QUADRO DE LEITURA
# ============================================================

def validar_quadro_leitura(inicio, posicao_stop):
    """
    Verifica se o STOP está no mesmo quadro de leitura do AUG.
    A distância entre START e STOP deve ser múltipla de 3.
    """

    if inicio == -1 or posicao_stop == -1:
        return False

    return (posicao_stop - inicio) % 3 == 0


# ============================================================
# VALIDAÇÃO COMPLETA DO mRNA
# ============================================================

def validar_mrna(mrna):

    # --------------------------------------------------------
    # 1. VALIDAR CAP 5'
    # --------------------------------------------------------

    if not validar_cap(mrna):

        return {
            "status": "ERRO",
            "resultado": "BUG - CAP 5'",
            "proteina": None
        }

    # --------------------------------------------------------
    # 2. VALIDAR CAUDA POLI-A
    # --------------------------------------------------------

    if not validar_cauda_poli_a(mrna):

        return {
            "status": "ERRO",
            "resultado": "BUG - cauda poli-A",
            "proteina": None
        }

    # --------------------------------------------------------
    # 3. REMOVER CAP
    # --------------------------------------------------------

    sequencia = remover_cap(mrna)

    # --------------------------------------------------------
    # 4. REMOVER CAUDA POLI-A
    # --------------------------------------------------------

    sequencia = remover_cauda_poli_a(sequencia)

    # --------------------------------------------------------
    # 5. VALIDAR BASES DO RNA
    # --------------------------------------------------------

    if not validar_bases_rna(sequencia):

        return {
            "status": "ERRO",
            "resultado": "BUG - sequência RNA inválida",
            "proteina": None
        }

    # --------------------------------------------------------
    # 6. LOCALIZAR O PRIMEIRO AUG
    # --------------------------------------------------------

    inicio = encontrar_start(sequencia)

    if inicio == -1:

        return {
            "status": "ERRO",
            "resultado": "BUG - START ausente",
            "proteina": None
        }

    # --------------------------------------------------------
    # 7. PROCURAR STOP EM FASE
    # --------------------------------------------------------

    posicao_stop, codon_stop = encontrar_stop_em_fase(
        sequencia,
        inicio
    )

    # --------------------------------------------------------
    # 8. SE NÃO ENCONTROU STOP EM FASE
    # --------------------------------------------------------

    if posicao_stop == -1:

        if existe_stop_fora_de_fase(sequencia, inicio):

            return {
                "status": "ERRO",
                "resultado": "BUG - quadro de leitura",
                "proteina": None
            }

        return {
            "status": "ERRO",
            "resultado": "BUG - STOP ausente",
            "proteina": None
        }

    # --------------------------------------------------------
    # 9. VALIDAR QUADRO DE LEITURA
    # --------------------------------------------------------

    quadro_valido = validar_quadro_leitura(
        inicio,
        posicao_stop
    )

    if not quadro_valido:

        return {
            "status": "ERRO",
            "resultado": "BUG - quadro de leitura",
            "proteina": None
        }

    # --------------------------------------------------------
    # 10. EXTRAIR REGIÃO CODIFICANTE
    # --------------------------------------------------------

    sequencia_codificante = sequencia[
        inicio:posicao_stop + 3
    ]

    # --------------------------------------------------------
    # 11. mRNA VALIDADO
    # --------------------------------------------------------

    return {
        "status": "OK",
        "resultado": "CORRETO",

        "cap": CAP_5,

        "start": "AUG",
        "inicio": inicio,

        "stop": codon_stop,
        "fim": posicao_stop,

        "quadro_leitura": "OK",

        "sequencia_codificante": sequencia_codificante,

        "proteina": None
    }