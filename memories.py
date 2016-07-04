# -*- coding: utf-8 -*-
import mimetypes

from bson import ObjectId
from flask import Flask, render_template, send_from_directory, request
from flask_assets import Environment, Bundle
from flask.ext.pymongo import PyMongo

from jsonify import jsonify
import datetime


app = Flask(__name__)
mongo = PyMongo(app)
assets = Environment(app)


js = Bundle('js/jquery-2.2.4.js', 'js/underscore-1.8.3.js', 'js/backbone-1.3.3.js', 'js/backbone.computedfields-0.0.12.js', 'js/backbone-mediator.js', 'js/moment-2.13.0.js',
            'js/linear-partition.js', 'js/templates/tool-bar.js', 'js/templates/modal.js', 'js/gallery.js',
            filters='jsmin', output='packed.js')
css = Bundle('css/reset.css', 'css/style.css', filters='cssmin', output='packed.css')
assets.register('js_all', js)
assets.register('css_all', css)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/photo/<string:image_id>')
def show_photo(image_id):
    return render_template('photo.html', photo=mongo.db.pictures.find_one_or_404({'_id': ObjectId(image_id)}))


@app.route('/thumbnail/<path:filename>')
def thumbnail(filename):
    return send_from_directory('/home/stephan/Images/.memories/thumbnails', filename, mimetype=mimetypes.guess_type('/home/stephan/Images/.memories/thumbnails/%s' % filename)[0])


@app.route('/image/<path:filename>')
def image(filename):
    return send_from_directory('/home/stephan/Images', filename, mimetype=mimetypes.guess_type('/home/stephan/Images/%s' % filename)[0])


@app.route('/api/v1/images')
def images():
    return jsonify(list(get_pictures(page=int(request.args.get('page', 1)))))


@app.route('/api/v1/images/<string:image_id>', methods=['DELETE'])
def delete_image(image_id):
    mongo.db.pictures.update_one({'_id': ObjectId(image_id)}, {'$set': {'delete': True, 'deleted': datetime.datetime.now()}})
    return '', 204


def get_pictures(page):
    size = 30
    return mongo.db.pictures.find({'mime_type': {'$regex': '^image/'}, 'delete': {'$ne': True}}).sort('shot', -1).skip(size * (page - 1)).limit(size)


if __name__ == '__main__':
    app.run(debug=True)
