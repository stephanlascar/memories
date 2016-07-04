# -*- coding: utf-8 -*-
import hashlib
import os
import shutil
import sqlite3
import unicodedata
import datetime

import exifread
from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient()
    db = client.memories

    with sqlite3.connect('/home/stephan/Bibliothèque Photos.photoslibrary/database/Library.apdb') as conn:
        for row in conn.execute('select modelId, uuid, orientation, name, createDate, isInTrash, inTrashDate, isMissing, fileName, imagePath, imageDate, width, height from RKMaster'):
            with open(u'/home/stephan/Bibliothèque Photos.photoslibrary/Masters/%s' % unicodedata.normalize('NFKC', row[9]), 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
                exif = exifread.process_file(f, details=False)
                try:
                    date = datetime.datetime.strptime(exif['EXIF DateTimeOriginal'].values, '%Y:%m:%d %H:%M:%S')
                except KeyError:
                    date = datetime.datetime.strptime('2001:01:01', '%Y:%m:%d') + datetime.timedelta(seconds=float(row[10]))
                filename = os.path.basename(f.name)

            new_dir = u'/home/stephan/Images/%s/%04d-%02d-%02d' % (date.year, date.year, date.month, date.day) if date else u'/home/stephan/Images/trier'
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)

            try:
                resolution = (exif['EXIF ExifImageWidth'].values[0], exif['EXIF ExifImageLength'].values[0])
            except KeyError:
                resolution = (row[11], row[12])

            inserted = modified = datetime.datetime.now()

            shutil.copy2(u'/home/stephan/Bibliothèque Photos.photoslibrary/Masters/%s' % unicodedata.normalize('NFKC', row[9]), new_dir)
            filename_in_library = '%s/%04d-%02d-%02d/%s' % (date.year, date.year, date.month, date.day, os.path.basename(u'/home/stephan/Bibliothèque Photos.photoslibrary/Masters/%s' % unicodedata.normalize('NFKC', row[9])))

            picture = dict(filename=filename_in_library, checksum=md5, shot=date.isoformat(), resolution=dict(width=resolution[0], height=resolution[1]), inserted=inserted.utcnow().isoformat(), modified=modified.utcnow().isoformat())
            db.pictures.insert_one(picture)
