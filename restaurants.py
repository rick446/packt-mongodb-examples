from flask import Flask
from flask import request, Response
from bson.json_util import dumps

from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo()


def main():
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
    mongo.init_app(app)
    app.run(debug=True)


@app.route('/restaurant/<cuisine>')
def get_restaurant_by_cuisine(cuisine):
    curs = mongo.db.restaurants.find({'cuisine': cuisine})
    total = curs.count()
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 50))
    curs = curs.skip(skip)
    curs = curs.limit(limit)
    response = dict(
        skip=skip,
        limit=limit,
        total=total,
        items=list(curs))
    return Response(
        dumps(response, indent=True),
        mimetype='application/json')



if __name__ == '__main__':
    main()
