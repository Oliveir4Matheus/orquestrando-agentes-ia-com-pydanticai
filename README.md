# Orquestrando Agentes de IA com PydanticAI

**Autor: Oliveir4Matheus**

![Capa do livro Orquestrando Agentes de IA com PydanticAI](capa/02-orquestrando-agentes-ia-manga-colorido.png)

Este é um livro didático e prático, escrito em português do Brasil, sobre a construção de agentes de inteligência artificial com **Python**, **Pydantic** e **PydanticAI**. O percurso começa nos fundamentos — modelos, ferramentas, mensagens, validação e contexto — e avança até arquiteturas de orquestração, sistemas multiagente, memória, RAG, segurança, avaliação e operação em produção.

A proposta não é apenas mostrar agentes conversando. Ao longo do livro, você aprende a projetar sistemas capazes de consultar informações, executar ações, dividir responsabilidades, colaborar, pedir aprovação humana e explicar o caminho percorrido. Os exemplos evoluem em pequenos degraus, do concreto ao abstrato, e incluem código executável, modelos simulados, erros comuns, testes e recapitulações.

O conteúdo é indicado para pessoas que já conhecem o básico de Python e desejam compreender como agentes funcionam por dentro. Não é necessário dominar Pydantic nem ter experiência anterior com sistemas multiagente: o Módulo 0 prepara toda a base utilizada nos capítulos seguintes.

## O que você aprenderá

- distinguir chatbots, workflows e agentes;
- criar agentes com instruções, ferramentas, dependências e saídas tipadas;
- administrar contexto, histórico e memória de curto e longo prazo;
- aplicar prompting, RAG e ajuste fino no problema adequado;
- combinar encadeamento, roteamento, paralelização e ciclos de avaliação;
- projetar equipes de agentes, supervisores, transferências e diferentes topologias;
- adicionar guardrails, permissões e aprovação humana às ações de maior risco;
- avaliar respostas, trajetórias e uso de ferramentas;
- observar, executar e manter agentes com mais segurança em produção.

O livro utiliza uma loja fictícia chamada **Casa Verde** como fio condutor. Dessa forma, os conceitos crescem sobre um domínio conhecido, sem trocar todo o contexto a cada capítulo.

## Sumário

| Módulo | Capítulos | Assunto |
| --- | --- | --- |
| [0 — Fundamentos de Pydantic e PydanticAI](modulo-00/00-visao-geral.md) | 0.1 a 0.7 | ecossistema; Python que o livro assume; Pydantic na prática; o primeiro agente por dentro; mensagens e testes sem API; ferramentas e saída tipada; dependências e contexto |
| [1 — O que é um agente](modulo-01/00-visao-geral.md) | 1 a 4 | chatbot, workflow e agente; modelo, ferramentas e instruções; camada de orquestração; quando construir |
| [2 — O ciclo de raciocínio e ação](modulo-02/00-visao-geral.md) | 5 a 7 | ReAct; cadeia e árvore de pensamentos; Reflexion |
| [3 — Engenharia de contexto e memória](modulo-03/00-visao-geral.md) | 8 a 10 | contexto finito, poda e resumo; notas e recuperação sob demanda; arquitetura de memória |
| [4 — Uso de ferramentas](modulo-04/00-visao-geral.md) | 11 a 13 | contrato da ferramenta; interface agente-computador; ações em JSON ou em código |
| [5 — Prompting, RAG e ajuste fino](modulo-05/00-visao-geral.md) | 14 a 17 | escada de customização; RAG; LoRA; ancoragem |
| [6 — Padrões de orquestração de um agente](modulo-06/00-visao-geral.md) | 18 a 21 | encadeamento, roteamento, paralelização, orquestrador-trabalhadores, avaliador-otimizador, blocos combináveis |
| [7 — Orquestração multiagente](modulo-07/00-visao-geral.md) | 22 a 26 | gerente e transferência; orquestrador em produção; supervisor e colaboradores; topologias; MCP e A2A |
| [8 — Guardrails, segurança e supervisão humana](modulo-08/00-visao-geral.md) | 27 a 29 | guardrails em camadas; risco por ferramenta; humano no ciclo |
| [9 — Avaliação de agentes](modulo-09/00-visao-geral.md) | 30 a 33 | tarefas e avaliadores; trajetória; juízes; benchmarks e avaliação contínua |
| [10 — Confiabilidade e operação em produção](modulo-10/00-visao-geral.md) | 34 a 37 | observabilidade; execução durável; avaliação em produção; deploy gerenciado |

Cada módulo é uma pasta com um arquivo `00-visao-geral.md`, um arquivo por capítulo, as imagens em `img/` e **todo o código dos capítulos em `codigo/`**: os blocos de código do texto são idênticos aos arquivos dessa pasta, e foram executados.

## Como executar os exemplos

Requisitos: Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install "pydantic-ai-slim[anthropic,mcp]" fastmcp pydantic-evals logfire
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

O modelo usado nos exemplos está em um único lugar, o arquivo `config.py` de cada módulo (`MODELO = "anthropic:claude-sonnet-5-5"`). Para usar outro provedor, troque essa linha e defina a chave correspondente.

Os exemplos com **modelo simulado** (arquivos `*_simulado.py` e `*_demo.py`) não precisam de chave nem de rede e produzem exatamente a saída mostrada no livro. Os demais chamam um modelo real, e o texto gerado varia de execução para execução; o livro avisa quando isso acontece.

## As imagens

As ilustrações foram geradas com o Gemini, pela linha de comando `agy`. O manifesto com a descrição de cada uma está em `ferramentas/imagens.json`. Para gerar as que ainda não existem:

```bash
python ferramentas/gerar_imagens.py
```

O script pula as imagens já existentes, usa três processos em paralelo e alterna entre as contas `agy` e `agy02` quando a cota de uma delas esgota.

## Fontes

Cada capítulo termina com a lista das fontes das quais o conteúdo foi extraído (artigos, guias técnicos e documentação), e todo o texto é original, escrito no padrão da skill. A documentação do PydanticAI usada como referência está na pasta `docs/`, na raiz do projeto.

## Contribuições

Se este livro ajudou você, considere apoiar sua continuidade. Toda contribuição é voluntária e ajuda a manter o conteúdo gratuito, atualizado e disponível para estudo.

Escaneie o QR Code abaixo para contribuir via Pix:

<img src="qrcode-pix.png" alt="QR Code para contribuição via Pix" width="280">

## Licença

Este livro é disponibilizado sob uma **Licença de Uso Educacional e Não Comercial**.

Você pode, gratuitamente:

- ler, baixar e armazenar uma cópia do livro;
- utilizar o conteúdo para estudo pessoal, pesquisa e atividades educacionais não comerciais;
- citar pequenos trechos, desde que o autor e a obra sejam devidamente creditados;
- compartilhar o livro gratuitamente, sem alterações e mantendo esta licença e os créditos do autor.

Você **não pode**:

- vender o livro, no todo ou em parte, em formato físico ou digital;
- cobrar pelo acesso, download ou distribuição do conteúdo;
- incluir o livro ou partes substanciais dele em cursos, assinaturas, produtos, treinamentos ou serviços pagos;
- utilizar o conteúdo para promoção comercial, revenda, sublicenciamento ou qualquer forma de exploração econômica;
- remover os créditos do autor ou apresentar a obra como sendo de outra pessoa.

Em resumo: o uso e o estudo são livres, mas a comercialização é expressamente proibida. Os direitos autorais permanecem com **Oliveir4Matheus**. Qualquer utilização não prevista acima exige autorização prévia e expressa do autor.
