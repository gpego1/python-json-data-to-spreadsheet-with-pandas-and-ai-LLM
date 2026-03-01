# AI Order Analyzer 📊🤖

Este projeto é um **analisador de pedidos com IA** que lê um arquivo JSON contendo pedidos de um e-commerce, utiliza um modelo de linguagem para estruturar os dados e gera automaticamente uma **planilha Excel (.xlsx)** com cada item de pedido organizado em linhas.

O objetivo é demonstrar um **pipeline simples de dados + IA**, que transforma dados brutos em um formato pronto para análise.

---

# Funcionalidades

* Leitura de pedidos a partir de um arquivo JSON
* Processamento e estruturação dos dados
* Integração com modelo de IA via API
* Conversão automática para DataFrame com pandas
* Geração de planilha Excel
* Estrutura preparada para análise de dados

---

# Estrutura do Projeto

```
ai-analyzer/
│
├── src/
│   └── models/
│       └── mock/
│           └── orders.json
│
├── main.py
├── .env
├── requirements.txt
└── README.md
```

---

# Exemplo de JSON de Entrada

```json
{
  "orders": [
    {
      "id": 1,
      "produtos": [
        { "nome": "Teclado", "quantidade": 1, "preco": 350 },
        { "nome": "Mouse", "quantidade": 2, "preco": 100 }
      ],
      "preco_total": 550
    }
  ]
}
```

---

# Resultado Gerado

O sistema gera um arquivo:

```
orders.xlsx
```

Com a estrutura:

| order_id | product_name | quantity | unit_price | total_order_price |
| -------- | ------------ | -------- | ---------- | ----------------- |
| 1        | Teclado      | 1        | 350        | 550               |
| 1        | Mouse        | 2        | 100        | 550               |

---

# Tecnologias Utilizadas

* Python
* Pandas
* OpenAI API
* JSON
* OpenPyXL
* Python Dotenv

---

# Instalação

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/ai-order-analyzer.git
cd ai-order-analyzer
```

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente:

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

# Configuração

Crie um arquivo `.env` na raiz do projeto:

```
OPENAI_API_KEY=your_api_key
BASE_URL=your_api_url
MODEL=your_model_name
```

---

# Como Executar

```bash
python main.py
```

Após executar, será gerado:

```
orders.xlsx
```

---

# Possíveis Melhorias

* Dashboard automático
* Insights de vendas com IA
* Detecção de padrões de compra
* Geração de relatórios automáticos
* Upload de arquivos JSON via interface
* API para análise de pedidos

---

# Objetivo do Projeto

Este projeto foi criado para demonstrar:

* Integração entre **IA e engenharia de dados**
* Processamento de dados com Python
* Estruturação de dados para análise
* Construção de projetos para portfólio de tecnologia
