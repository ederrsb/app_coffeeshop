from flask import Blueprint, jsonify, request
from functools import wraps
from conexao_db import Conexao
from logger import logger
import bcrypt
import jwt  # Adicione esta importação

login_bp = Blueprint('login', __name__)
conexao = Conexao()
chave_secreta = "kmdghb9D0knSTD790410MnalE5s"  # Substitua pela sua chave secreta

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
        hash_senha = usuario[6]  # O índice 6 é assumido com base na estrutura da tabela

        # Verifica se a senha fornecida coincide com a senha armazenada
        if hash_senha and bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8')):
            # Senhas coincidem, gera o token JWT
            token_payload = {
                'id_usuario': usuario[0],  # Substitua pelo índice correto se necessário
                'email': usuario[5]  # Substitua pelo índice correto se necessário
            }
            token = jwt.encode(token_payload, chave_secreta, algorithm='HS256')

            # Retorna o token no formato JSON
            return jsonify({'token': token, 'message': 'Login bem-sucedido'}), 200
        else:
            # Senhas não coincidem, retorno de falha
            return jsonify({'message': 'Credenciais inválidas'}), 401

    except Exception as e:
        logger.error(f"Erro durante o login: {str(e)}")
        return jsonify({'message': 'Erro durante o login'}), 500

def verifica_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token não fornecido'}), 401

        try:
            # Verifique se o token está no formato correto
            if not token.startswith('Bearer '):
                raise jwt.InvalidTokenError("Token inválido")

            token = token.split(' ')[1]
            payload = jwt.decode(token, chave_secreta, algorithms=['HS256'])
            # Adicione o payload decodificado aos argumentos da função
            return f(payload, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401

    return decorator