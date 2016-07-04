# -*- coding: utf-8 -*-
import mimetypes
from unqlite import UnQLite
from pymongo import MongoClient
import dateutil.parser


if __name__ == "__main__":
    db = UnQLite('./memories.db')
    pictures = db.collection('pictures')
    client = MongoClient()
    db = client.memories

    for picture in pictures.all():
        del(picture['__id'])
        picture['modified'] = dateutil.parser.parse(picture['modified'])
        picture['date'] = dateutil.parser.parse(picture['date'])
        picture['inserted'] = dateutil.parser.parse(picture['inserted'])


        db.pictures.insert_one(picture)
        print picture
