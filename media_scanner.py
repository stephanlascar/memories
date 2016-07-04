# -*- coding: utf-8 -*-
import hashlib
import os
from unqlite import UnQLite
import exifread
import datetime


db = UnQLite('./memories.db')
pictures = db.collection('pictures')
pictures.create()
pictures.store({'name': 'Leslie', 'color': 'also green'})
print pictures.fetch(0)


if __name__ == '__main__':
    for dirpath, dirs, files in os.walk('/home/stephan/Images/2015'):
        for filename in files:
            with open(os.path.join(dirpath, filename), 'rb') as fname:
                exif = exifread.process_file(fname, details=False)
                photo_date = datetime.datetime.strptime(exif['EXIF DateTimeOriginal'].values, '%Y:%m:%d %H:%M:%S')
                resolution = (exif['EXIF ExifImageWidth'].values[0], exif['EXIF ExifImageLength'].values[0])
                inserted = modified = datetime.datetime.now()
                md5 = hashlib.md5(fname.read()).hexdigest()

                print filename
                print photo_date
                print resolution
                print inserted
                print modified
                print md5
                print '------------------'

                exit