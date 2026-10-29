# EcoAção

<p align="center">
  <strong>Conhecer os problemas ambientais é o primeiro passo para transformar a realidade.</strong>
  <br />
  Uma plataforma que conecta informações sobre o meio ambiente a pessoas e iniciativas que buscam protegê-lo.
</p>

---

## Sobre o projeto

O **EcoAção** é um projeto de plataforma web criado com o objetivo de facilitar o acesso a informações sobre as mudanças climáticas e aproximar as pessoas de organizações que trabalham para proteger o meio ambiente.

Muitas pessoas sabem que as mudanças climáticas são um problema, mas não conhecem suas principais causas, como elas afetam sua região ou quais iniciativas estão trabalhando para mudar essa realidade.

O EcoAção busca ajudar a responder a essas perguntas por meio de duas funcionalidades principais: um diagnóstico ambiental por região e um diretório de organizações ambientais.

## Funcionalidades

### 1. Diagnóstico ambiental por região

O usuário poderá pesquisar uma cidade ou região e consultar informações sobre os principais fatores que contribuem para as emissões de gases de efeito estufa naquele local.

Mas o que isso significa?

Gases de efeito estufa são gases presentes na atmosfera que retêm parte do calor da Terra. Eles fazem parte do funcionamento natural do planeta, mas o aumento de sua concentração, causado principalmente por atividades humanas, intensifica o aquecimento global.

Entre as atividades que podem contribuir para essas emissões estão a produção de energia, as indústrias, a agricultura e o descarte de resíduos.

O diagnóstico pretende reunir dados disponíveis sobre esses fatores e apresentá-los de maneira visual e fácil de compreender, utilizando gráficos, indicadores e explicações.

**Exemplo:** ao pesquisar uma região, o usuário poderá visualizar quais setores aparecem como fontes relevantes de emissões nos dados consultados e entender melhor sua contribuição para o problema.

A precisão das informações dependerá das fontes disponíveis. Quando não houver dados específicos da cidade, a plataforma deverá informar essa limitação, em vez de apresentar estimativas como se fossem números exatos.

### 2. Diretório de ONGs e iniciativas ambientais

O EcoAção também pretende reunir informações sobre organizações não governamentais (ONGs) e iniciativas que atuam na preservação ambiental.

Essas organizações podem trabalhar com reflorestamento, proteção de animais, conservação de florestas, educação ambiental, reciclagem e combate às mudanças climáticas.

A plataforma permitirá que o usuário encontre informações como:

- Nome e descrição da organização.
- Região onde atua.
- Principais projetos e causas defendidas.
- Site oficial e canais públicos de contato.
- Formas de participação, como voluntariado e campanhas ambientais.

**Objetivo:** facilitar o encontro entre pessoas que desejam contribuir com o meio ambiente e organizações que já desenvolvem esse trabalho.

As informações serão reunidas a partir de fontes públicas e verificadas sempre que possível.

## Como o sistema vai funcionar?

O funcionamento pode ser entendido em cinco etapas:

1. **O usuário pesquisa:** informa a cidade ou região que deseja conhecer.
2. **O sistema busca informações:** consulta fontes de dados ambientais disponíveis.
3. **Os dados são organizados:** o sistema separa as informações relevantes e prepara os indicadores.
4. **Os resultados são apresentados:** o usuário visualiza gráficos e explicações sobre os desafios ambientais da região.
5. **O usuário encontra iniciativas:** pode consultar o diretório de ONGs e descobrir formas de participar de ações ambientais.

Essas etapas serão realizadas por diferentes partes do sistema, que trabalham em conjunto para transformar dados encontrados em fontes externas em informações úteis para o usuário.

## Tecnologias planejadas

As tecnologias abaixo são ferramentas que poderão ser utilizadas para construir a plataforma. Cada uma terá uma função específica.

| Tecnologia | Para que será utilizada? |
|---|---|
| React | Criar a interface do site, incluindo páginas, menus, gráficos e áreas de pesquisa. |
| TypeScript | Ajudar a escrever um código mais organizado e identificar determinados erros durante o desenvolvimento. |
| Vite | Facilitar a criação, os testes e a preparação do site para publicação. |
| Python | Implementar a lógica do sistema, como organizar os dados e preparar os resultados. |
| FastAPI | Criar a comunicação entre a interface do site, o processamento dos dados e o banco de dados. |
| PostgreSQL | Armazenar informações organizadas, como os dados cadastrados sobre as organizações ambientais. |
| PostGIS | Adicionar recursos de consulta geográfica ao banco de dados, caso sejam necessários. |

Essa é a arquitetura inicialmente planejada. As tecnologias definitivas poderão mudar conforme as necessidades do projeto.

## APIs e fontes de dados

Para apresentar informações ambientais e geográficas, o EcoAção poderá utilizar fontes externas.

Uma **API** é uma forma padronizada de dois sistemas trocarem informações. Por exemplo, o EcoAção poderá solicitar dados a um serviço externo e utilizar as informações recebidas para montar um gráfico no site.

Algumas fontes que serão avaliadas:

### Climate TRACE

Site: https://climatetrace.org/

É uma iniciativa que reúne dados e estimativas sobre emissões de gases de efeito estufa em diferentes setores e regiões.

**Como poderá ajudar:** fornecer informações para o diagnóstico ambiental, permitindo analisar fontes de emissão e comparar os dados disponíveis.

A disponibilidade de dados detalhados para cada município e as condições de acesso precisarão ser verificadas.

### OpenStreetMap

Site: https://www.openstreetmap.org/

É um projeto colaborativo que reúne informações geográficas, como ruas, localidades e outros elementos do mapa.

**Como poderá ajudar:** fornecer referências geográficas para localizar cidades e organizar informações relacionadas a diferentes regiões.

### Nominatim

Documentação: https://nominatim.org/release-docs/latest/api/Overview/

É um serviço que permite pesquisar lugares a partir de nomes ou endereços e obter informações geográficas correspondentes.

**Como poderá ajudar:** permitir que o usuário digite o nome de uma cidade e que o sistema identifique a localização correspondente.

O uso do serviço deverá respeitar suas regras e limites de utilização.

### IPCC

Site: https://www.ipcc.ch/

O Painel Intergovernamental sobre Mudanças Climáticas reúne avaliações científicas sobre as mudanças climáticas, suas causas, seus impactos e possíveis formas de enfrentamento.

**Como poderá ajudar:** servir como referência científica para explicar os conceitos ambientais apresentados pela plataforma e fundamentar o conteúdo informativo.

O IPCC é principalmente uma fonte científica, não uma API que fornece automaticamente todos os dados necessários ao sistema.

### Cadastro de organizações ambientais

Não será presumida a existência de uma única API que reúna todas as ONGs ambientais brasileiras com informações completas e atualizadas.

Por isso, a proposta inicial é criar um cadastro próprio, preenchido com informações públicas encontradas nos sites oficiais das organizações.

Esse cadastro poderá armazenar os nomes, as áreas de atuação, as regiões atendidas e os links para os canais oficiais de cada iniciativa.

## Como as partes do sistema se conectam?

O projeto terá três componentes principais:

```text
Usuário
   |
   v
Site (React)
Interface com páginas, pesquisas e gráficos
   |
   v
Backend (Python + FastAPI)
Organiza informações e processa solicitações
   |
   +------> Fontes externas de dados
   |
   +------> Banco de dados (PostgreSQL)
   |
   v
Resultados enviados ao site
```

**Site (frontend):** é a parte que o usuário vê e utiliza. É onde estarão os campos de pesquisa, os gráficos e as informações sobre as organizações.

**Backend:** é a parte responsável pela lógica do sistema. Recebe as solicitações feitas pelo site, consulta as fontes necessárias, organiza os dados e devolve os resultados.

**Banco de dados:** funciona como um local organizado para guardar informações que o próprio projeto precisa manter, como o cadastro de ONGs e outros dados de referência.

Essa separação ajuda a manter o projeto organizado e facilita a adição de novas funcionalidades no futuro.

## Confiabilidade e privacidade

O EcoAção pretende apresentar informações ambientais de forma responsável.

- Os dados deverão indicar suas fontes e, quando possível, a data de referência.
- Números estimados serão identificados como estimativas.
- A plataforma informará quando não houver dados suficientes para uma análise local confiável.
- As informações sobre organizações serão conferidas em fontes oficiais sempre que possível.
- A pesquisa por cidade não exigirá necessariamente a localização exata do usuário.
- A coleta de informações pessoais será limitada ao necessário para o funcionamento da plataforma.

## Status do projeto

**Em planejamento e desenvolvimento.**

As funcionalidades, tecnologias e integrações descritas neste README representam a proposta inicial do EcoAção. Elas serão implementadas e testadas ao longo do desenvolvimento.

## Contribuições

Ideias, sugestões e melhorias poderão contribuir para a evolução do projeto. As instruções para instalação, execução e contribuição serão adicionadas quando a estrutura do código estiver definida.

## Licença

A licença será definida pelos responsáveis pelo projeto.

---

<p align="center">
  <strong>EcoAção</strong>
  <br />
  Informação para compreender. Iniciativa para transformar.
</p>









<img width="296" height="326" alt="image" src="https://github.com/user-attachments/assets/d6509b15-2dec-44c6-b1ac-a3165bd2dce5" />
