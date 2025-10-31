# Crie o arquivo: alembic/env.py
# (Substitua todo o conteúdo)

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

# --- Nossas Modificações ---
# 1. Importar a Base dos nossos models
# (Alembic precisa saber quais tabelas queremos criar)
from api.models import Base 

# 2. Carregar o .env para ler a DATABASE_URL
load_dotenv()
# --- Fim das Modificações ---


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- Nossa Modificação ---
# 3. Força o Alembic a usar a DATABASE_URL do .env
#    Isto é crucial para o Render (produção) e local (dev)
db_url = os.getenv("DATABASE_URL")
if not db_url:
    # Se não achar no .env, usa o fallback do alembic.ini
    db_url = config.get_main_option("sqlalchemy.url")
config.set_main_option("sqlalchemy.url", db_url)
# --- Fim da Modificação ---


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# target_metadata = None
# --- Nossa Modificação ---
# 4. Aponta para os nossos models
target_metadata = Base.metadata
# --- Fim da Modificação ---

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    (Conteúdo padrão, não precisa mexer)
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    (Conteúdo padrão, não precisa mexer)
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.QueuePool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()