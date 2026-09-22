from dataclasses import dataclass
from typing import Optional #O optional é utilizado, pois quando ocorre algum erro, nem todas essas informações existem, então cada campo pode ter um str ou pode ficar sem valor


@dataclass # Classe para guardar dados sem precisar escrever construtor manualmente, cada mRNA processado vai gerar um objeto desse tipo
class ResultadoProcessamento:
    linha: int
    status: str
    resultado: str
    proteina: Optional[str] = None

    cap: Optional[str] = None
    start: Optional[str] = None
    quadro_leitura: Optional[str] = None
    stop: Optional[str] = None
    cauda_poli_a: Optional[str] = None
    traducao: Optional[str] = None