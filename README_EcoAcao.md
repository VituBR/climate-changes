# EcoAção

**Conhecimento ambiental para transformar realidades.**

O EcoAção é uma aplicação web desenvolvida para facilitar o acesso a informações sobre emissões de gases de efeito estufa e aproximar os usuários de organizações que atuam na preservação ambiental.

A plataforma permite pesquisar localidades, consultar estimativas de emissões por país e ano, visualizar informações organizadas por setor e encontrar ou cadastrar ONGs ambientais.

## Objetivos do projeto

- Facilitar a consulta de informações sobre emissões de gases de efeito estufa.
- Apresentar dados ambientais de forma organizada e compreensível.
- Permitir a busca de cidades e regiões.
- Reunir informações sobre ONGs e iniciativas ambientais.
- Incentivar a conscientização e a participação em ações de preservação.

## Funcionalidades implementadas

### 1. Pesquisa de localidades

O usuário pode informar o nome de uma cidade ou região. A aplicação consulta o serviço Nominatim, do OpenStreetMap, e apresenta os locais encontrados para seleção.

A pesquisa utiliza informações geográficas disponibilizadas pelo serviço externo. A disponibilidade dos resultados depende dos dados cadastrados no OpenStreetMap.

### 2. Diagnóstico de emissões

Após selecionar uma localidade, o sistema consulta a API do Climate TRACE para obter dados de emissões associados ao país correspondente.

O diagnóstico apresenta estimativas de emissões de gases de efeito estufa e sua divisão por setores, como:

- Energia elétrica;
- Transportes;
- Agropecuária;
- Indústria;
- Operações de combustíveis fósseis;
- Edificações;
- Resíduos;
- Mineração;
- Florestas e uso do solo;
- Gases fluorados.

O sistema permite consultar anos de 2015 a 2024. O ano padrão da consulta é 2024.

**Importante:** a pesquisa começa por uma cidade ou região, mas os dados de emissões consultados são referentes ao país identificado. Portanto, os resultados não devem ser interpretados como medições específicas daquela cidade.

### 3. Diretório de ONGs ambientais

A aplicação possui um diretório de organizações ambientais armazenadas em um banco de dados local.

É possível:

- Consultar as ONGs cadastradas;
- Pesquisar organizações por nome, descrição, causas ou região;
- Cadastrar uma nova ONG;
- Informar nome, descrição, causas, região, site e formas de participação;
- Visualizar organizações relacionadas à região pesquisada, conforme as informações cadastradas.

Os cadastros são armazenados localmente no SQLite. O sistema informa quando uma organização ainda não foi verificada. O cadastro não significa que a organização tenha sido validada oficialmente.

### 4. Página de fontes

A aplicação possui uma página que apresenta as fontes de dados utilizadas e informações sobre suas limitações.

### 5. Tratamento de erros

O sistema apresenta páginas específicas para erros de requisição e páginas não encontradas. Também trata falhas de comunicação com os serviços externos, evitando que uma consulta malsucedida seja apresentada como se tivesse sido concluída normalmente.

## Como o sistema funciona

1. **Pesquisa:** o usuário informa uma cidade ou região.
2. **Geolocalização textual:** o Nominatim retorna localidades compatíveis com a pesquisa.
3. **Seleção:** o usuário escolhe uma das localidades encontradas.
4. **Consulta ambiental:** o sistema identifica o país e consulta a API do Climate TRACE.
5. **Processamento:** o Python organiza os dados recebidos e separa as informações por setor.
6. **Apresentação:** o site exibe o diagnóstico e as ONGs relacionadas à região, quando houver cadastros compatíveis.

## Tecnologias e bibliotecas utilizadas

| Tecnologia ou biblioteca | Função no projeto |
|---|---|
| Python | Linguagem utilizada na lógica da aplicação e no processamento dos dados. |
| Flask | Framework responsável pelas rotas, requisições, respostas e renderização das páginas. |
| Requests | Realiza as consultas HTTP às APIs externas. |
| SQLite3 | Banco de dados local utilizado para armazenar as ONGs. Faz parte da biblioteca padrão do Python. |
| HTML | Estrutura as páginas da aplicação. |
| CSS | Define a aparência, cores, espaçamentos e organização visual do site. |
| Jinja2 | Motor de templates utilizado pelo Flask para gerar páginas HTML dinâmicas. É instalado como dependência do Flask. |
| Threading e ThreadPoolExecutor | Recursos da biblioteca padrão do Python utilizados no controle de concorrência das tarefas. |

O projeto também utiliza módulos da biblioteca padrão do Python, como `os`, `re`, `time`, `sqlite3` e `urllib.parse`, sem necessidade de instalá-los separadamente.

## APIs e fontes de dados

- [Climate TRACE](https://climatetrace.org/) — fornece estimativas de emissões de gases de efeito estufa. A aplicação consulta sua API para obter os dados utilizados no diagnóstico.
- [OpenStreetMap](https://www.openstreetmap.org/) — projeto colaborativo de dados geográficos utilizado como fonte pelo serviço de pesquisa de localidades.
- [Nominatim](https://nominatim.org/release-docs/latest/api/Overview/) — serviço utilizado para pesquisar localidades e obter informações como país, estado e cidade.
- [IPCC](https://www.ipcc.ch/) — referência científica sobre mudanças climáticas. É uma fonte de consulta e contextualização, não uma API integrada diretamente ao código atual.

A disponibilidade dos dados depende dos serviços externos, de suas políticas de uso e da cobertura das informações fornecidas. Os resultados do Climate TRACE são estimativas e devem ser interpretados de acordo com a metodologia e as limitações da fonte.

## Requisitos

Para executar o projeto, é necessário ter:

- Python 3.10 ou superior;
- pip, gerenciador de pacotes do Python;
- Acesso à internet para consultar o Nominatim e o Climate TRACE.

As dependências externas do projeto estão listadas no arquivo `requirements.txt`:

```text
Flask>=3.0
requests>=2.31
```

As demais bibliotecas utilizadas são nativas do Python ou instaladas automaticamente como dependências do Flask.

## Como instalar e executar

### 1. Baixe ou clone o projeto

Abra o terminal na pasta que contém o arquivo `app.py`.

### 2. Crie um ambiente virtual (recomendado)

No Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

No Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
python app.py
```

### 5. Acesse o site

Com o servidor iniciado, abra o navegador e acesse:

```text
http://127.0.0.1:5000
```

Para encerrar o servidor, pressione `Ctrl + C` no terminal.

## Configurações opcionais

O projeto permite configurar algumas opções por variáveis de ambiente:

| Variável | Finalidade |
|---|---|
| `ECOACAO_CONTATO` | Identifica o contato utilizado no User-Agent das consultas ao Nominatim. Configure um contato válido antes de utilizar o serviço. |
| `ECOACAO_SECRET` | Define a chave secreta utilizada pelo Flask. Recomenda-se configurar uma chave própria em ambientes de implantação. |
| `CLIMATETRACE_BASES` | Permite definir as versões-base da API do Climate TRACE que serão tentadas pela aplicação. Por padrão, são utilizadas as versões v7 e v6. |

## Estrutura do projeto

```text
EcoAção/
│
├── app.py                 # Aplicação Flask, rotas e lógica principal
├── iso_countries.py       # Conversão de códigos de países ISO 2 para ISO 3
├── ecoacao.db             # Banco de dados SQLite das ONGs
├── requirements.txt       # Dependências externas do Python
├── test_app.py            # Testes automatizados
│
├── templates/             # Páginas HTML renderizadas pelo Flask
│   ├── base.html
│   ├── index.html
│   ├── buscar.html
│   ├── diagnostico.html
│   ├── ongs.html
│   ├── ong_form.html
│   ├── fontes.html
│   └── erro.html
│
└── static/
    └── style.css          # Estilos da aplicação
```

## Testes

O projeto possui testes automatizados em `test_app.py`. Eles podem ser executados com:

```bash
python -m unittest -v
```

Os testes utilizam simulações de respostas externas em determinadas verificações, permitindo testar partes da aplicação sem depender de consultas reais às APIs.

## Limitações e confiabilidade das informações

- Os dados de emissões apresentados são estimativas fornecidas pelo Climate TRACE.
- A consulta de emissões é feita por país, mesmo quando a pesquisa inicial é por cidade ou região.
- A cobertura e a atualização dos dados dependem das fontes externas.
- O Nominatim depende das informações disponíveis no OpenStreetMap.
- As ONGs são armazenadas em um banco de dados local e seus cadastros não são automaticamente verificados por uma entidade oficial.
- A aplicação depende de conexão com a internet para realizar consultas às APIs externas.

## Status do projeto

**Em desenvolvimento.** A aplicação já possui pesquisa de localidades, consulta de estimativas de emissões, diretório local de ONGs, cadastro de organizações e páginas de apresentação das fontes e de erros.

---

**EcoAção — Entender os desafios ambientais é o primeiro passo para mudar o futuro.**
