# -*- coding: utf-8 -*-
import os
from unqlite import UnQLite
from PIL import Image
import rawpy
from pymongo import MongoClient


if __name__ == '__main__':
    client = MongoClient()
    db = client.memories
    pictures = db.pictures.find({'thumbnail': {'$exists': False}})

    if not os.path.exists('/home/stephan/Images/.memories/thumbnails'):
        os.makedirs('/home/stephan/Images/.memories/thumbnails')

    for picture in pictures:
        try:
            im = Image.open('/home/stephan/Images/%s' % picture.get('filename'))
            im.thumbnail((640, 480))

            if not os.path.exists(os.path.dirname('/home/stephan/Images/.memories/thumbnails/%s' % picture.get('filename'))):
                os.makedirs(os.path.dirname('/home/stephan/Images/.memories/thumbnails/%s' % picture.get('filename')))

            try:
                filename = picture.get('filename')
                im.save('/home/stephan/Images/.memories/thumbnails/%s' % filename)
            except KeyError as nef:
                print 'raw file %s' % picture.get('filename')
                raw = rawpy.imread('/home/stephan/Images/%s' % picture.get('filename'))
                rbg = raw.postprocess()
                img = Image.fromarray(rbg)
                filename = '%s.jpg' % os.path.splitext(picture.get('filename'))[0]
                img.save('%s.jpg' % (os.path.splitext('/home/stephan/Images/.memories/thumbnails/%s' % picture.get('filename'))[0]))

            print filename
            db.pictures.update_one({'_id': picture['_id']}, {"$set": {'thumbnail': filename}})

        except IOError as e:
            print e
            print picture.get('filename')
            print '---------------------'
            print '---------------------'
            print '---------------------'
            print '---------------------'