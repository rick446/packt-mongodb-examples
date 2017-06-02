from flask import Flask
from flask import request, Response
from bson.json_util import dumps

from . import model

app = Flask('packt-blog')
model.mongo.init_app(app)


def jsonify(doc):
    return Response(
        dumps(doc, indent=True),
        mimetype='application/json')


@app.route('/post')
def get_posts():
    return jsonify(model.find_posts())


@app.route('/post', methods=['POST'])
def create_post():
    post = model.create_post(request.json)
    return jsonify(post)


@app.route('/post/<ObjectId:post_id>')
def get_post(post_id):
    return jsonify(model.get_post(post_id))


@app.route('/post/<ObjectId:post_id>')
def update_post(post_id):
    post = model.update_post(post_id, request.json)
    return jsonify(post)


@app.route('/post/<ObjectId:post_id>', methods=['DELETE'])
def delete_post(post_id):
    return '', 204


@app.route('/comment/<ObjectId:comment_id>')
def create_comment(post_id, body):
    return jsonify(model.create_comment(post_id, request.json))


@app.route('/author/<ObjectId:author_id>')
def get_author(author_id):
    return jsonify(model.get_comment(author_id))

