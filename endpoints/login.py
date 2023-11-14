from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
import bcrypt

login_bp = Blueprint('login', __name__)
conexao = Conexao()

@login_bp.route('/login', methods=['POST'])
def login_usuario():
    try:
        dados_login = request.get_json()

        email = dados_login.get('email')
        senha = dados_login.get('senha')

        if not email or not senha:
            return jsonify({'message': 'Email e senha são obrigatórios'}), 400

        # Consulta o usuário com base no email
        query = "SELECT * FROM usuario WHERE email = %s AND status = 'A'"
        params = (email,)

        # Supondo que você está usando execute_query que retorna uma lista de tuplas
        resultados = conexao.execute_query(query, params)

        # Certifique-se de que há pelo menos um resultado na lista
        if not resultados:
            return jsonify({'message': 'Usuário não encontrado'}), 404

        # Pegue o primeiro resultado
        usuario = resultados[0]

        # Ajuste para tratar os resultados corretamente
        hash_senha = usuario[6]  # O índice 6 é assumido com base na estrutura da tabela

        # Verifica se a senha fornecida coincide com a senha armazenada
        if hash_senha and bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8')):
            # Senhas coincidem, retorno bem-sucedido
            return jsonify({'message': 'Login bem-sucedido'}), 200
        else:
            # Senhas não coincidem, retorno de falha
            return jsonify({'message': 'Credenciais inválidas'}), 401

    except Exception as e:
        logger.error(f"Erro durante o login: {str(e)}")
        return jsonify({'message': 'Erro durante o login'}), 500
