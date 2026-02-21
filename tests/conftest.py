"""Configuração raiz de testes: carrega variáveis de ambiente do .env.test antes de qualquer import
e impede que o load_dotenv() carregue o .env local durante a execução dos testes."""

import os
from pathlib import Path
from unittest.mock import patch

from dotenv import load_dotenv

# Carrega o .env.test explicitamente
env_path = Path(__file__).parent.parent / ".env.test"
load_dotenv(dotenv_path=env_path)

# Mocka chamadas futuras ao load_dotenv para que o .env de dev não sobrescreva o de teste
patch("dotenv.load_dotenv", return_value=None).start()
