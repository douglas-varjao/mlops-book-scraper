# Crie o arquivo: scripts/create_admin.py
# E cole este código:

import os
import logging
import sys
from dotenv import load_dotenv

# Ajusta o path para que o script possa achar a pasta 'api'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Carrega as variáveis do arquivo .env (da raiz do projeto)
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Importa os componentes da API
from api.database import SessionLocal, engine
from api.models import Base, User
from api.security import get_password_hash # Importa a função de hashear senha

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_initial_admin():
    # Garante que a tabela 'users' exista (ela foi criada pelo 'alembic upgrade head')
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Pega os dados de login do admin do arquivo .env
        username = os.getenv("INIT_ADMIN_USERNAME")
        email = os.getenv("INIT_ADMIN_EMAIL")
        password = os.getenv("INIT_ADMIN_PASSWORD")

        if not all([username, email, password]):
            logger.error("ERRO: Variáveis de admin (INIT_ADMIN_...) não estão no .env.")
            logger.error("Por favor, copie .env.example para .env e preencha.")
            return

        # Verifica se o admin já existe (pelo username ou email)
        existing_admin = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_admin:
            logger.warning(f"Usuário admin '{username}' ou email '{email}' já existe. Nenhuma ação tomada.")
            return

        # Se não existe, cria o novo admin
        logger.info(f"Criando usuário admin: {username} ({email})")
        hashed_password = get_password_hash(password) # Criptografa a senha
        
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=True # Define como admin
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logger.info(f"Usuário admin '{username}' criado com sucesso.")
        
    except Exception as e:
        logger.error(f"Erro ao criar admin inicial: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_admin()