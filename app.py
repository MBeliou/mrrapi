
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, url_for
from flask_restful import abort, Api, Resource
from mrr_api import MrrApi as mrr

ALGO_LIST = [
    'scrypt',
    'sha256',
]

app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

# Shows the lowest price for a single algo
class return_lowest(Resource):
    def get(self, algo):
        if algo not in ALGO_LIST:
            abort(404, message="Algo {} isn't supported".format(algo))
        else:
            out = mrr('2ffa0754242ab89607a986672e3f532ebd41c14c29cd6d1785c59b205ca97c13','feed83a2629f09418a53433705701f68a1bce13363896d8ef24d11c91200f9b0').cheapest_rig(algo)
            return out

class return_list(Resource):
    def get(self):
        algo = request.args.get('algo')
        if algo not in ALGO_LIST:
            abort(404, message="Algo {} isn't supported".format(algo))
        else:
            out = mrr('2ffa0754242ab89607a986672e3f532ebd41c14c29cd6d1785c59b205ca97c13','feed83a2629f09418a53433705701f68a1bce13363896d8ef24d11c91200f9b0').rig_list(algo)
            return out

## Setup the Api resource routing here

api.add_resource(return_lowest, '/api/cheapest/<algo>')
api.add_resource(return_list,'/api/list')

if __name__ == "__main__":
    app.run(debug=False)