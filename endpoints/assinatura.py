from flask import Blueprint, jsonify
from conexao_db import Conexao

assinatura_bp = Blueprint('assinatura', __name__)

conexao = Conexao()

@assinatura_bp.route('/assinaturas', methods=['GET'])
def obter_assinaturas():
    query = 'SELECT * FROM assinatura'
    resultado = conexao.execute_query(query)

    if resultado:
        colunas = [column[0] for column in conexao.cursor.description]
        assinaturas = [dict(zip(colunas, assinatura)) for assinatura in resultado]
        return jsonify(assinaturas)
    else:
        return jsonify([])

@assinatura_bp.route('/assinaturas/<int:id_assinatura>', methods=['GET'])
def obter_assinatura(id_assinatura):
    query = 'SELECT * FROM assinatura WHERE id_assinatura = %s'
    resultado = conexao.execute_query(query, (id_assinatura,))

    if resultado:
        colunas = [column[0] for column in conexao.cursor.description]
        assinatura = dict(zip(colunas, resultado[0]))
        return jsonify(assinatura)
    else:
        return jsonify({'message': 'Assinatura não encontrada'}), 404
