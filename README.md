BioCompiler 3.0 — Ribossomo / Protein Translator

Projeto desenvolvido para a disciplina de Tópicos em Bioinformática, representando a terceira etapa do fluxo BioCompiler.

O BioCompiler 3.0 recebe um mRNA maduro produzido pelo BioCompiler 2.0 e simula, de forma didática, sua tradução em uma sequência de aminoácidos.

🧬 Fluxo do BioCompiler

BioCompiler 1.0
DNA → pré-mRNA

BioCompiler 2.0
pré-mRNA → mRNA maduro

BioCompiler 3.0
mRNA maduro → proteína

Nesta etapa, o Ribossomo realiza:

mRNA maduro
    ↓
Validar CAP 5'
    ↓
Validar cauda poli-A
    ↓
Validar bases A/U/G/C
    ↓
Localizar o primeiro AUG
    ↓
Ler códons em trincas
    ↓
Localizar STOP em fase
    ↓
Traduzir códons
    ↓
Gerar proteína

🎯 Objetivo

O programa deve:

receber um ou mais mRNAs maduros;

validar sua estrutura;

identificar a região codificante;

localizar o primeiro códon de iniciação AUG;

realizar a leitura em grupos de três nucleotídeos;

localizar o primeiro códon STOP em fase;

converter os códons em aminoácidos;

gerar a sequência proteica quando a entrada for válida;

emitir um diagnóstico quando houver erro.

A tradução termina na geração da sequência de aminoácidos. O projeto não simula dobramento proteico, modificações pós-traducionais ou destino celular da proteína.

⚙️ Regras implementadas

CAP 5'

A sequência deve começar exatamente com:

m7Gppp

Cauda poli-A

A extremidade 3' deve possuir exatamente 100 adeninas consecutivas.

Bases válidas

Após a remoção da CAP e da cauda poli-A, a sequência deve conter somente:

A U G C

START

A tradução começa no primeiro AUG encontrado.

Além de iniciar a tradução, AUG codifica:

Met

Leitura

A partir do START, a sequência é lida de 3 em 3 bases.

Exemplo:

AUG | GCU | AAA | CCG | UAA

STOP

Os códons de parada são:

UAA
UAG
UGA

Eles encerram a tradução e não adicionam aminoácidos à proteína.

Representação dos aminoácidos

Os aminoácidos são representados pelo código de três letras.

Exemplo:

AUG | GCU | AAA | CCG | UAA
 ↓     ↓     ↓     ↓
Met   Ala   Lys   Pro

Resultado:

Met-Ala-Lys-Pro

🧪 Casos reconhecidos

Caso

Situação

Resultado

1

mRNA maduro válido e traduzível

CORRETO

2

CAP 5' ausente ou diferente de m7Gppp

BUG - CAP 5'

3

Códon de iniciação AUG ausente

BUG - START ausente

4

STOP em fase ausente

BUG - STOP ausente

5

Região codificante incompatível com leitura em trincas

BUG - quadro de leitura

6

Cauda poli-A ausente, alterada ou diferente de 100 A

BUG - cauda poli-A

O backend também valida caracteres inválidos na região de RNA e, nesse caso, retorna:

BUG - sequência RNA inválida

📁 Estrutura atual do projeto

Biocompiler-3.0-Ribossomo-do-RNA-maduro-ate-a-proteina/
│
├── app.py
├── README.md
├── plano-de-fundo-do-dia-nacional-da-ciencia_23-2149283127.avif
│
├── backend/
│   ├── conversao.py
│   ├── main.py
│   ├── modelos.py
│   ├── processamento.py
│   ├── traducao.py
│   └── validacao.py
│
└── dados/
    ├── entradas_vindas_do_biocompiler_2.0.txt
    ├── entrada_ribossomo.txt
    └── resultados.txt

🧩 Organização do backend

backend/conversao.py

Converte a saída do BioCompiler 2.0 para o formato utilizado internamente pelo Ribossomo.

O arquivo vindo do BioCompiler 2.0 possui campos separados por ;, incluindo:

linha;status;resultado;mRNA_maduro

A conversão mantém apenas os registros em que:

status = OK

e em que:

mRNA_maduro != NÃO GERADO

Os mRNAs válidos são então gravados em:

dados/entrada_ribossomo.txt

com uma sequência por linha.

backend/validacao.py

Responsável pela validação estrutural do mRNA.

Verifica:

CAP 5';

cauda poli-A;

bases A/U/G/C;

primeiro AUG;

STOP em fase;

quadro de leitura.

Quando o mRNA é válido, também fornece a região codificante para a etapa de tradução.

backend/traducao.py

Contém o código genético utilizado pelo programa e transforma a região codificante em aminoácidos.

A leitura é feita em trincas e termina ao encontrar:

UAA
UAG
UGA

backend/modelos.py

Define a estrutura utilizada para representar cada resultado do processamento.

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

status da tradução.

backend/processamento.py

Integra validação, tradução e geração dos resultados.

Possui funções para:

processar um único mRNA;

processar todas as entradas de um arquivo;

salvar os resultados em arquivo texto.

backend/main.py

Executa o fluxo completo do backend:

saída do BioCompiler 2.0
        ↓
conversao.py
        ↓
entrada_ribossomo.txt
        ↓
processamento
        ↓
validação
        ↓
tradução
        ↓
resultados.txt

A conversão é executada automaticamente antes do processamento.

📥 Entrada

Saída recebida do BioCompiler 2.0

O arquivo utilizado pelo backend é:

dados/entradas_vindas_do_biocompiler_2.0.txt

Ele possui registros como:

linha;status;resultado;mRNA_maduro
1;ERRO;...;NÃO GERADO
2;OK;CORRETO;m7Gppp...AAAAAAAA

Somente os registros que realmente geraram um mRNA maduro são encaminhados para a etapa do Ribossomo.

Entrada interna do Ribossomo

Após a conversão, é gerado:

dados/entrada_ribossomo.txt

No formato:

m7GpppSEQUENCIA_DE_RNA + cauda poli-A

com um mRNA por linha.

📤 Saída

O resultado final é salvo em:

dados/resultados.txt

com o cabeçalho:

linha;status;resultado;proteina

Exemplo:

1;OK;CORRETO;Met-Ala-Lys-Pro
2;ERRO;BUG - CAP 5';NÃO GERADA
3;ERRO;BUG - START ausente;NÃO GERADA

🖥️ Interface gráfica

A interface foi desenvolvida com Streamlit e utiliza a imagem:

plano-de-fundo-do-dia-nacional-da-ciencia_23-2149283127.avif

como plano de fundo.

A aplicação apresenta:

visão geral do Ribossomo;

métricas das entradas;

tabela de resultados;

detalhamento individual;

diagnóstico de cada etapa;

destaque visual de CAP, START, STOP e cauda poli-A;

proteína gerada quando aplicável;

download dos resultados.

A interface consegue interpretar:

o formato oficial do Ribossomo, com um mRNA por linha;

a saída do BioCompiler 2.0, filtrando automaticamente os registros que realmente geraram mRNA maduro.

🚀 Como executar

1. Clonar o repositório

git clone https://github.com/MonnikLuianne/Biocompiler-3.0-Ribossomo-do-RNA-maduro-ate-a-proteina.git

Entre na pasta:

cd Biocompiler-3.0-Ribossomo-do-RNA-maduro-ate-a-proteina

2. Instalar as dependências da interface

Atualmente, as dependências externas utilizadas pelo front são:

python -m pip install streamlit pandas

3. Executar o backend completo

Na raiz do projeto:

python -m backend.main

Esse comando:

converte a saída do BioCompiler 2.0
→ gera entrada_ribossomo.txt
→ processa os mRNAs
→ exibe os resultados
→ gera resultados.txt

4. Executar a interface gráfica

Na raiz do projeto:

python -m streamlit run app.py

📊 Conjunto de dados atualmente presente no projeto

No arquivo atualmente utilizado como saída do BioCompiler 2.0 existem 40 registros.

Desses registros, 10 possuem status = OK e um mRNA_maduro efetivamente gerado. Portanto, são esses 10 que seguem para o Ribossomo.

Os demais registros não são analisados pelo BioCompiler 3.0 porque não produziram um mRNA maduro na etapa anterior.

No conjunto atual, os 10 mRNAs encaminhados ao Ribossomo não possuem o códon de iniciação AUG. Por isso, o resultado produzido para todos eles é:

BUG - START ausente

Esse comportamento corresponde aos dados atuais e não representa erro de execução do Ribossomo.

🧠 Resumo do funcionamento

BioCompiler 2.0
      ↓
seleciona mRNAs realmente gerados
      ↓
BioCompiler 3.0
      ↓
CAP válida?
      ↓
100 A na cauda?
      ↓
bases válidas?
      ↓
AUG existe?
      ↓
STOP em fase existe?
      ↓
traduz códons
      ↓
proteína

🛠️ Tecnologias utilizadas

Python 3

Streamlit

Pandas

dataclasses

módulo csv

Git e GitHub

📚 BioCompiler 3.0

Ribossomo — Protein Translator

Da mensagem genética à proteína.