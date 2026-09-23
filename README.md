BioCompiler 3.0 — Ribossomo / Protein Translator

📌 Sobre o projeto

O BioCompiler 3.0 — Ribossomo / Protein Translator é a terceira etapa do projeto BioCompiler, desenvolvido para a disciplina de Tópicos em Bioinformática.

Nesta fase, o objetivo é simular de forma didática o processo de tradução de um mRNA maduro em uma sequência de aminoácidos, reproduzindo o papel do ribossomo.

O sistema recebe mRNAs maduros produzidos pelo BioCompiler 2.0, valida sua estrutura, identifica a região codificante, realiza a leitura dos códons e gera a proteína correspondente quando a entrada é válida.

🧬 Fluxo do BioCompiler

BioCompiler 1.0
DNA → pré-mRNA
        ↓
BioCompiler 2.0
pré-mRNA → mRNA maduro
        ↓
BioCompiler 3.0
mRNA maduro → proteína

No BioCompiler 3.0, o fluxo principal é:

mRNA maduro
    ↓
Validar CAP 5'
    ↓
Validar cauda poli-A
    ↓
Validar bases A/U/G/C
    ↓
Localizar primeiro AUG
    ↓
Ler códons em trincas
    ↓
Localizar STOP em fase
    ↓
Traduzir códons
    ↓
Gerar proteína

⚙️ Funcionalidades

O sistema é capaz de:

Ler um ou vários mRNAs maduros;

Converter automaticamente a saída do BioCompiler 2.0 para o formato utilizado pelo Ribossomo;

Validar a presença da CAP 5' (m7Gppp);

Validar a cauda poli-A com exatamente 100 adeninas;

Validar se a sequência contém somente as bases A, U, G e C;

Localizar o primeiro códon de iniciação AUG;

Ler a região codificante em grupos de três nucleotídeos;

Localizar o primeiro códon STOP em fase:

UAA

UAG

UGA

Traduzir os códons utilizando o código genético;

Representar aminoácidos pelo código de três letras;

Gerar a proteína no formato:

Met-Ala-Lys-Pro

Identificar erros estruturais no mRNA;

Processar várias entradas em lote;

Exibir os resultados em uma interface gráfica desenvolvida com Streamlit;

Exportar os resultados em arquivo .txt.

🧪 Casos reconhecidos

O sistema reconhece os seguintes casos:

Caso

Situação

Resultado

1

mRNA válido e traduzível

CORRETO

2

CAP 5' ausente ou incorreta

BUG - CAP 5'

3

AUG ausente

BUG - START ausente

4

STOP em fase ausente

BUG - STOP ausente

5

Região incompatível com o quadro de leitura

BUG - quadro de leitura

6

Cauda poli-A inválida

BUG - cauda poli-A

📁 Estrutura do projeto

Biocompiler-3.0-Ribossomo-do-RNA-maduro-ate-a-proteina/
│
├── app.py
├── requirements.txt
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── conversao.py
│   ├── processamento.py
│   ├── validacao.py
│   ├── traducao.py
│   └── modelos.py
│
├── dados/
│   ├── entradas_vindas_do_biocompiler_2.0.txt
│   ├── entrada_ribossomo.txt
│   └── resultados.txt
│
└── assets/
    └── imagem de fundo da interface

A organização exata da pasta assets pode variar de acordo com o nome utilizado para a imagem de fundo.

🧩 Organização do backend

validacao.py

Responsável por validar a estrutura do mRNA.

Verifica:

CAP 5';

cauda poli-A;

bases válidas;

START;

STOP;

quadro de leitura.

traducao.py

Responsável pela tradução da região codificante.

Contém:

estrutura de dados com o código genético;

códons STOP;

função que percorre a sequência de 3 em 3;

conversão dos códons em aminoácidos.

Exemplo:

AUG | GCU | AAA | CCG | UAA
 ↓     ↓     ↓     ↓
Met   Ala   Lys   Pro

Resultado:

Met-Ala-Lys-Pro

modelos.py

Define a estrutura utilizada para representar cada resultado processado.

Entre os dados armazenados estão:

número da entrada;

status;

resultado;

proteína;

CAP;

START;

STOP;

quadro de leitura;

cauda poli-A;

estado da tradução.

processamento.py

É responsável por integrar as etapas do backend.

Fluxo:

mRNA
 ↓
validacao.py
 ↓
traducao.py
 ↓
modelos.py
 ↓
resultado

Também realiza:

processamento de uma única entrada;

processamento em lote;

exportação do arquivo de resultados.

conversao.py

Converte a saída do BioCompiler 2.0 para o formato esperado pelo Ribossomo.

Exemplo de saída do BioCompiler 2.0:

linha;status;resultado;mRNA_maduro
1;ERRO;BUG - sítio 3' ausente;NÃO GERADO
2;OK;CORRETO;m7Gppp...AAAAAAAA

Após a conversão:

m7Gppp...AAAAAAAA

Somente registros com status = OK e mRNA realmente gerado são encaminhados ao Ribossomo.

main.py

Executa o fluxo completo do backend:

BioCompiler 2.0
      ↓
conversão
      ↓
entrada do Ribossomo
      ↓
validação
      ↓
tradução
      ↓
relatório
      ↓
resultados.txt

🖥️ Interface gráfica

A interface foi desenvolvida utilizando Streamlit.

Ela apresenta:

visão geral do Ribossomo / Protein Translator;

métricas das entradas;

execução do processamento;

tabela de resultados;

detalhamento individual das entradas;

diagnóstico dos erros;

informações sobre CAP, START, STOP, quadro de leitura e cauda poli-A;

proteína gerada;

opção de download dos resultados.

A interface utiliza uma identidade visual própria do BioCompiler 3.0, mantendo inspiração visual nas fases anteriores do projeto.

📥 Formato de entrada do Ribossomo

O formato esperado internamente é:

m7GpppSEQUENCIA_DE_RNAAAAAAAAA...AAAAAAAA

Cada linha representa um mRNA independente.

A cauda poli-A deve conter exatamente 100 adeninas consecutivas.

Exemplo conceitual:

m7GpppCCAUGGCUAAACCGUAAGGAAAAAAAA...(100 A)

📤 Formato da saída

O arquivo de resultados utiliza campos separados por ;.

linha;status;resultado;proteina

Exemplo:

1;OK;CORRETO;Met-Ala-Lys-Pro
2;ERRO;BUG - CAP 5';NÃO GERADA
3;ERRO;BUG - START ausente;NÃO GERADA

🚀 Como executar

1. Clone o repositório

git clone https://github.com/MonnikLuianne/Biocompiler-3.0-Ribossomo-do-RNA-maduro-ate-a-proteina.git

Entre na pasta:

cd Biocompiler-3.0-Ribossomo-do-RNA-maduro-ate-a-proteina

2. Instale as dependências

python -m pip install -r requirements.txt

3. Executar apenas o backend

Na raiz do projeto:

python -m backend.main

O programa realiza automaticamente:

conversão
→ processamento
→ validação
→ tradução
→ geração de resultados

4. Executar a interface gráfica

Na raiz do projeto:

python -m streamlit run app.py

O Streamlit abrirá a aplicação no navegador.

🧠 Exemplo de tradução

Entrada codificante:

AUGGCUAAACCGUAA

Separação dos códons:

AUG | GCU | AAA | CCG | UAA

Tradução:

AUG → Met
GCU → Ala
AAA → Lys
CCG → Pro
UAA → STOP

Proteína:

Met-Ala-Lys-Pro

O códon STOP encerra a tradução e não é adicionado à sequência de aminoácidos.

🛠️ Tecnologias utilizadas

Python 3

Streamlit

Pandas

Dataclasses

CSV

Git / GitHub

🎯 Objetivo didático

O objetivo do projeto é representar computacionalmente o processo de tradução molecular, associando conceitos de Bioinformática e Biologia Molecular a técnicas de programação.

O programa não simula:

dobramento proteico;

modificações pós-traducionais;

transporte celular;

destino celular da proteína.

O processamento termina na geração da sequência de aminoácidos.

👨‍💻 Execução resumida

Para rodar o sistema completo pela interface:

python -m streamlit run app.py

Para testar somente o backend:

python -m backend.main

📚 BioCompiler 3.0

Ribossomo — Protein Translator

Da mensagem genética à proteína.