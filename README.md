# Sistema Financeiro Simplificado

Sistema de controle financeiro com gestão de contas, categorias, transações, pessoas e pagamentos.

## Tecnologias

- **FastAPI** - Framework web moderno e rápido para Python
- **PostgreSQL** - Banco de dados relacional
- **psycopg2** - Driver PostgreSQL para Python

## Configuração

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar banco de dados

Edite o arquivo `core/settings.py` com as credenciais do seu banco PostgreSQL:

```python
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_NAME = "sistema_financeiro_simplificado"
```

### 3. Criar banco de dados e tabelas

Execute o script SQL para criar as tabelas:

```bash
psql -U postgres -d sistema_financeiro_simplificado -f database/schema.sql
```
Ou execute o script o arquivo create_table.py:

```bash
python create_table.py
```

Ou crie o banco primeiro e depois execute o script:

```bash
createdb -U postgres sistema_financeiro_simplificado
psql -U postgres -d sistema_financeiro_simplificado -f database/schema.sql
```

### 4. Executar a aplicação

```bash
uvicorn main:app --reload
```

A API estará disponível em: `http://localhost:8000`

Documentação interativa (Swagger): `http://localhost:8000/docs`

## Estrutura da API

### Recursos Principais

Todos os recursos possuem operações CRUD completas:

- **Contas** (`/contas`) - Gerenciamento de contas bancárias
- **Categorias** (`/categorias`) - Categorias de receitas e despesas
- **Transações** (`/transacoes`) - Registro de movimentações financeiras
- **Pessoas** (`/pessoas`) - Clientes e fornecedores
- **Pagamentos** (`/pagamentos`) - Controle de status de pagamentos

### Soft Delete

Todos os recursos utilizam **soft delete** (desativação). Em vez de deletar, use:

```
PATCH /{recurso}/{id}/desativar
```

Isso define `ativo=false` sem remover o registro do banco.

### Filtros

Todos os endpoints GET aceitam query parameters opcionais para filtragem:

- **Contas**: `?nome=...&ativo=true`
- **Categorias**: `?nome=...&tipo=receita&ativo=true`
- **Transações**: `?conta_id=1&categoria_id=2&data_ini=2025-11-01&data_fim=2025-11-30&ativo=true`
- **Pessoas**: `?nome=...&tipo=cliente&ativo=true`
- **Pagamentos**: `?transacao_id=1&status=pago&data_ini=...&data_fim=...&ativo=true`

### Relatórios

Endpoints de relatórios disponíveis em `/relatorios`:

1. **Resumo Financeiro** - `/relatorios/resumo-financeiro`
   - Total de receitas, despesas e saldo final
   - Filtros: `data_ini`, `data_fim`, `conta_id`

2. **Transações por Categoria** - `/relatorios/transacoes-categoria`
   - Agrupamento de transações por categoria
   - Filtros: `categoria_id`, `data_ini`, `data_fim`

3. **Pagamentos Pendentes** - `/relatorios/pagamentos-pendentes`
   - Lista todos os pagamentos com status pendente

4. **Saldo por Conta** - `/relatorios/contas-saldo`
   - Receitas, despesas e saldo calculado por conta
   - Filtros: `data_ini`, `data_fim`

## Exemplos de Uso

### Criar uma conta

```bash
POST /contas
{
  "nome": "Conta Corrente",
  "saldo_inicial": 1500.00
}
```

### Criar uma categoria

```bash
POST /categorias
{
  "nome": "Salário",
  "tipo": "receita"
}
```

### Criar uma transação

```bash
POST /transacoes
{
  "conta_id": 1,
  "categoria_id": 2,
  "valor": 250.00,
  "data": "2025-11-06T10:00:00Z",
  "descricao": "Pagamento de energia"
}
```

### Desativar um recurso

```bash
PATCH /contas/1/desativar
```

Retorna `204 No Content`.

## Validações

- `valor` deve ser maior que zero em transações
- `saldo_inicial` deve ser maior ou igual a zero em contas
- `tipo` deve ser válido conforme enum (`receita`/`despesa`, `cliente`/`fornecedor`)
- `data_pagamento` não pode ser anterior à `data` da transação
- Apenas recursos ativos podem ser referenciados em relacionamentos

## Formato de Datas

Todas as datas devem estar no formato ISO 8601:
- Data: `2025-11-06`
- Data e hora: `2025-11-06T14:00:00Z` ou `2025-11-06T14:00:00`

## Códigos de Resposta

- `200 OK` - Sucesso na requisição
- `201 Created` - Recurso criado com sucesso
- `204 No Content` - Operação bem-sucedida sem conteúdo (desativação)
- `400 Bad Request` - Erro de validação ou requisição inválida
- `404 Not Found` - Recurso não encontrado
