# FBD Project - FastAPI + psycopg2

Project created with ChatGPT. Contains endpoints for the following entities:
- Conta (account)
- Categoria (category)
- Transacao (transaction)
- Pessoa (person)
- Pagamento (payment)

Each entity has:
- GET /<entity>/ -> list all
- GET /<entity>/{id} -> get by id
- POST /<entity>/ -> create

## Setup

1. Create a Python virtual environment and activate it.
2. Install dependencies:
   pip install -r requirements.txt
3. Create a PostgreSQL database and update `.env` (see `.env.example`).
4. Run the SQL to create tables:
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f app/sql/init.sql
5. Start the server:
   uvicorn app.main:app --reload

