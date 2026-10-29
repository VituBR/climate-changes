# EcoAção

**Conhecimento ambiental para transformar realidades.**

O EcoAção é um projeto que busca conscientizar as pessoas sobre as mudanças climáticas e facilitar o acesso a informações sobre os problemas ambientais de diferentes regiões.

A plataforma pretende reunir informações sobre as emissões de gases de efeito estufa e conectar os usuários a ONGs e iniciativas que trabalham pela preservação do meio ambiente.

## Objetivos do projeto

- Informar sobre os principais fatores que contribuem para as mudanças climáticas em diferentes regiões.
- Apresentar informações ambientais de forma simples e visual.
- Facilitar a descoberta de ONGs e projetos de preservação ambiental.
- Incentivar a conscientização e a participação em iniciativas sustentáveis.

## Funcionalidades planejadas

### Diagnóstico ambiental regional

O usuário poderá pesquisar uma cidade ou região para consultar informações sobre os fatores que contribuem para as emissões de gases de efeito estufa.

Esses gases retêm calor na atmosfera. Quando sua concentração aumenta devido a atividades humanas, como a queima de combustíveis fósseis e determinadas atividades industriais, o aquecimento global se intensifica.

A plataforma pretende apresentar dados, gráficos e explicações para ajudar o usuário a compreender melhor os desafios ambientais de cada região.

A disponibilidade e a precisão das informações dependerão das fontes de dados utilizadas.

### Diretório de ONGs ambientais

A plataforma também pretende reunir informações sobre organizações e iniciativas que atuam na proteção do meio ambiente.

Os usuários poderão encontrar informações como:
- Nome e descrição da organização.
- Causas ambientais defendidas.
- Região de atuação.
- Site oficial e formas de participação.
- Projetos e iniciativas desenvolvidos.

O objetivo é aproximar pessoas interessadas em ajudar de organizações que já trabalham nessas causas.

## Como funcionará?

1. **Pesquisa:** o usuário informa a cidade ou região que deseja consultar.
2. **Busca de informações:** o sistema obtém os dados ambientais disponíveis.
3. **Processamento:** o Python organiza e processa as informações necessárias.
4. **Apresentação:** o site exibe os resultados de forma visual e compreensível.
5. **Conexão:** o usuário pode conhecer ONGs e descobrir iniciativas ambientais.

## Tecnologias utilizadas

| Tecnologia | Função no projeto |
|---|---|
| Python | Desenvolver a lógica do sistema e processar informações. |
| HTML | Construir a estrutura das páginas do site, como títulos, textos, links e seções. |
| CSS | Definir a aparência do site, incluindo cores, fontes, espaçamento e organização visual. |

O HTML estrutura o conteúdo, o CSS cuida da apresentação visual e o Python executa a lógica necessária para o funcionamento da aplicação.

## Fontes de dados

Para obter informações ambientais e geográficas, o projeto poderá utilizar fontes externas, dependendo da disponibilidade dos dados e das condições de acesso.

- [Climate TRACE](https://climatetrace.org/) — reúne dados e estimativas de emissões de gases de efeito estufa.
- [OpenStreetMap](https://www.openstreetmap.org/) — disponibiliza informações geográficas.
- [Nominatim](https://nominatim.org/release-docs/latest/api/Overview/) — permite pesquisar localidades e obter referências geográficas.
- [IPCC](https://www.ipcc.ch/) — fornece estudos e avaliações científicas sobre as mudanças climáticas.

As informações sobre ONGs poderão ser organizadas em um cadastro próprio, utilizando fontes públicas e sites oficiais.

A integração dessas fontes ainda dependerá da implementação. Nem todas disponibilizam os dados necessários para cada cidade, e algumas possuem regras específicas de utilização.

## Estrutura geral do sistema

```text
EcoAção
│
├── HTML
│   └── Estrutura das páginas
│
├── CSS
│   └── Aparência e organização visual
│
└── Python
    ├── Lógica da aplicação
    ├── Processamento de informações
    └── Busca e organização de dados
```

Essa estrutura representa a divisão básica das responsabilidades. A organização definitiva dos arquivos dependerá de como o código for desenvolvido.

## Confiabilidade das informações

O projeto busca apresentar informações ambientais de maneira responsável.

- Os dados deverão ter suas fontes identificadas.
- Estimativas serão diferenciadas de medições reais.
- Limitações na disponibilidade de informações serão comunicadas ao usuário.
- Os dados sobre organizações serão verificados em fontes oficiais sempre que possível.

## Status do projeto

**Em planejamento**

---

**EcoAção — Entender os desafios ambientais é o primeiro passo para mudar o futuro.**
