# 🚖 Sistema de Controle de Aplicativos para Motoristas

Sistema completo de controle financeiro para motoristas de aplicativos (Uber, 99, iFood, InDrive, Lalamove, Keeta).  
Registra turnos, ganhos, abastecimentos, controle de troca de óleo e exibe gráficos financeiros em tempo real.

**Criado por Vini Matos**

---

## 📁 Estrutura dos Módulos

O projeto está dividido em **6 arquivos Python**, cada um com uma responsabilidade clara.  
Quando precisar fazer alguma alteração, basta ir direto no módulo certo:

```
app-data/
│
├── main.py              ← Ponto de entrada (arquivo que o Streamlit executa)
├── config.py            ← Visual / Tema / CSS customizado
├── database.py          ← Conexão com o banco de dados Turso
├── utils.py             ← Funções auxiliares (senha, rodízio)
├── auth.py              ← Tela de Login e Cadastro de novos motoristas
├── dashboard.py         ← Painel principal (5 abas do sistema)
│
├── requirements.txt     ← Bibliotecas necessárias para rodar na nuvem
├── .gitignore           ← Arquivos que NÃO devem subir para o GitHub
└── README.md            ← Este arquivo de documentação
```

---

## 🔍 O que cada módulo faz

### `main.py` — Ponto de Entrada
- **O que faz:** É o "porteiro" do sistema. Ele é o arquivo que o Streamlit executa.
- **Como funciona:** Configura a página, aplica o tema visual, verifica se o usuário está logado. Se não estiver logado, mostra a tela de Login/Cadastro (`auth.py`). Se estiver logado, mostra o Painel (`dashboard.py`).
- **Quando mexer:** Quase nunca. Só se quiser trocar o título da página ou adicionar algo que apareça globalmente em todas as telas.

---

### `config.py` — Visual e Tema
- **O que faz:** Contém todo o CSS customizado (cores, botões, rodapé "by Vini Matos").
- **Como funciona:** Exporta a função `apply_custom_css()` que é chamada pelo `main.py` no início. Injeta HTML/CSS direto na página.
- **Quando mexer:** Quando quiser mudar cores dos botões, cor de fundo, tamanho de textos, aparência geral do aplicativo, ou trocar o nome no rodapé.

---

### `database.py` — Conexão com o Banco de Dados (Turso)
- **O que faz:** É o único arquivo que "fala" com o banco de dados Turso pela internet. Toda operação de leitura (SELECT) e escrita (INSERT, UPDATE, DELETE) passa por aqui.
- **Como funciona:** Exporta a função `executar_query(sql, params)`. Ela monta o JSON, manda a requisição HTTP para o Turso e devolve:
  - Uma **lista de tuplas** → quando a resposta traz dados (SELECT)
  - **True** → quando uma escrita (INSERT/UPDATE) funciona
  - **Lista vazia []** → quando dá erro (e exibe o erro na tela)
- **Quando mexer:** Se trocar de banco de dados, se trocar a URL ou o Token do Turso, ou se precisar adicionar logs de debug.

> ⚠️ **Segurança:** Na nuvem (Streamlit Cloud), o token é lido automaticamente do `Secrets`. Localmente, usa o token embutido como fallback.

---

### `utils.py` — Funções Utilitárias
- **O que faz:** Agrupa funções auxiliares "puras" que não dependem de tela.
- **Funções:**
  - `hash_senha(senha)` → Recebe uma senha em texto e devolve o hash SHA-256. Usado no login e cadastro.
  - `checar_rodizio(tipo, placa)` → Recebe o tipo do veículo e a placa, e diz se está em Rodízio em SP no dia de hoje. Motos são isentas.
- **Quando mexer:** Se quiser trocar o algoritmo de criptografia da senha, ou mudar as regras de rodízio (ex: adicionar outra cidade).

---

### `auth.py` — Tela de Login e Cadastro
- **O que faz:** Renderiza a tela inicial com duas abas: "Entrar" e "Criar Conta".
- **Como funciona:**
  - **Aba Entrar:** Pede usuário/senha, busca no banco. Se encontrar, salva na sessão e loga.
  - **Aba Criar Conta:** Valida o nome de usuário (sem espaço, sem maiúscula), valida a senha (8+ caracteres, maiúscula, número, especial), cria o usuário no banco e já cadastra o primeiro veículo junto.
- **Quando mexer:** Se quiser adicionar recuperação de senha, login por e-mail, mudar as regras de validação de senha, ou alterar o fluxo de cadastro.

---

### `dashboard.py` — Painel Principal (5 Abas)
- **O que faz:** Renderiza todo o painel do motorista logado. É o maior arquivo do projeto.
- **As 5 abas:**

| Aba | Função interna | O que faz |
|---|---|---|
| ⏱️ Turno Diário | `render_tab_turno()` | Inicia e encerra turnos de trabalho. Mostra o rodízio de SP. Salva KM inicial/final e gasto com alimentação. |
| 💰 Lançar Ganhos | `render_tab_ganhos()` | Registra o faturamento bruto por plataforma (Uber, 99, iFood, etc). |
| ⛽ Abastecimento | `render_tab_combustivel()` | Registra abastecimentos (valor, litros, KM). |
| 📈 Resumo Financeiro | `render_tab_graficos()` | Mostra os números (Bruto, Gastos, Lucro Líquido com %), gráfico de barras colorido por app e gráfico de pizza de gastos. Filtros por Hoje/Semana/Mês/Ano. |
| 🔧 Veículos & Óleo | `render_tab_manutencao()` | Mostra KM restantes para troca de óleo, botão de registrar troca, e formulário para adicionar novos veículos. |

- **Quando mexer:** Para adicionar novas abas, novos campos em abas existentes, mudar cores dos gráficos, ou adicionar novas plataformas de aplicativo.

---

## 🎨 Cores dos Aplicativos nos Gráficos

| Aplicativo | Cor | Hex |
|---|---|---|
| Uber | ⬛ Preto | `#000000` |
| 99 Moto/Carro | 🟨 Amarelo | `#FFD100` |
| iFood | 🟥 Vermelho | `#EA1D2C` |
| InDrive | 🟩 Verde Claro | `#A2F82F` |
| Lalamove | 🟧 Laranja | `#F37021` |
| Keeta | 🟩 Verde Limão | `#C6FF00` |
| Particular | ⬜ Cinza | `#888888` |

Para alterar, edite o dicionário `cores_apps` dentro de `render_tab_graficos()` em `dashboard.py`.

---

## 📦 Bibliotecas Utilizadas (requirements.txt)

| Biblioteca | Para que serve |
|---|---|
| `streamlit` | Framework web que gera toda a interface visual |
| `requests` | Faz as chamadas HTTP para a API do Turso (banco de dados) |
| `pandas` | Organiza os dados em tabelas para montar os gráficos |
| `plotly` | Renderiza os gráficos interativos (barras coloridas e pizza) |

---

## 🗄️ Tabelas no Banco de Dados (Turso)

| Tabela | O que armazena |
|---|---|
| `usuarios` | Login (usuario, senha_hash) |
| `veiculos` | Veículos do motorista (modelo, tipo, placa, KM, intervalo óleo) |
| `turnos` | Turnos de trabalho (data, KM inicial/final, gasto alimentação) |
| `ganhos` | Faturamento por plataforma (fonte, valor bruto, KM) |
| `combustivel` | Abastecimentos (valor pago, litros, KM) |
| `historico_manutencao` | Registro de trocas de óleo e manutenções |

