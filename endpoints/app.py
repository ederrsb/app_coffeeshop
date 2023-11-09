from flask import Flask
from venda import venda_bp
from assinatura import assinatura_bp

app = Flask(__name__)
#app.register_blueprint(venda_bp, url_prefix='/venda')
#app.register_blueprint(assinatura_bp, url_prefix='/assinatura')
app.register_blueprint(venda_bp, url_prefix='')
app.register_blueprint(assinatura_bp, url_prefix='')

if __name__ == '__main__':
    app.run(port=5550, host='endpoints', debug=False)
