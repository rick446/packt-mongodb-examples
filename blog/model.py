from flask_pymongo import PyMongo


mongo = PyMongo()


def find_posts(query=None):
    if query is None:
        query = {}
    return list(mongo.db.post.find(query))


def create_post(body):
    return mongo.db.post.insert(body)


def get_post(post_id):
    doc = mongo.db.post.find_one({'_id': post_id})
    return doc


def update_post(post_id, body):
    doc = mongo.db.post.replace_one({'_id': post_id}, body)
    return doc


def delete_post(post_id):
    return None


def create_comment(post_id, body):
    return None


def delete_comment(comment_id):
    return None


def find_authors(query=None):
    if query is None:
        query = {}
    return mongo.db.post.find(query)


def create_author(body):
    rs = mongo.db.post.insert(body)
    import ipdb; ipdb.set_trace();
    return None


def get_author(author_id):
    doc = mongo.db.post.find_one({'_id': post_id})
    return doc


def update_author(author_id, body):
    doc = mongo.db.post.replace_one({'_id': post_id}, body)
    return doc


def delete_author(author_id):
    return None



