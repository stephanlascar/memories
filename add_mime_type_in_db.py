# -*- coding: utf-8 -*-
import mimetypes
from unqlite import UnQLite
from pymongo import MongoClient

if __name__ == "__main__":
    client = MongoClient()
    db = client.memories

    for picture in db.pictures.find({'shot': {'$exists': True, '$ne': None}}):
        mime_type = mimetypes.guess_type('/home/stephan/Images/%s' % picture['filename'])[0]
        db.pictures.update({'_id': picture['_id']}, {'$set': {'mime_type': mime_type}})
