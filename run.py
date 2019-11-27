import flask
from apps import web_interface as multifeatures
from apps import single_chart as singlefeature

app = flask.Flask(__name__)

@app.route('/')
def home():
    return "<h1>Visit site MF or SF"

if __name__  == '__main__':
    app.run(host='localhost', port=8889, debug=True)