# -*- coding: utf-8 -*-
import os
import requests
from unqlite import UnQLite
import PIL
from PIL import Image



if __name__ == '__main__':
    db = UnQLite('./memories.db')
    pictures = db.collection('pictures')

    api_key = 'acc_1b6f09d173e4ae0'
    api_secret = 'ad7a71a02b8aef32c06aa7355e165ff7'
    image_path = '/home/stephan/Images/2010/2010-06-10/DSC_0314.JPG'

    for picture in pictures.filter(lambda obj: 'tags' not in obj):
        image_path = '/home/stephan/Images/%s' % picture['filename']
        _, file_extension = os.path.splitext(image_path)

        basewidth = 300
        img = Image.open(image_path)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        img.save('/tmp/resize_image%s' % file_extension)

        upload_response = requests.post('https://api.imagga.com/v1/content',
                                 auth=(api_key, api_secret),
                                 files={'image': open('/tmp/resize_image%s' % file_extension, 'r')})
        content_id = upload_response.json().get('uploaded')[0].get('id')

        tag_response = requests.get('https://api.imagga.com/v1/tagging?&content=%s' % content_id,  auth=(api_key, api_secret))
        print tag_response.json()
        tags = ([tag['tag'] for tag in tag_response.json().get('results')[0].get('tags') if tag['confidence'] >= 30])

        cathegories_response = requests.get('https://api.imagga.com/v1/categorizations/personal_photos?&content=%s' % content_id, auth=(api_key, api_secret))
        categories = ([categorie['name'] for categorie in cathegories_response.json().get('results')[0].get('categories') if categorie['confidence'] >= 30])

        picture['tags'] = tags
        picture['categories'] = categories
        pictures.update(picture['__id'], picture)
        print tag_response.status_code
        print picture
        print '----------------------------------------------------'
        print '----------------------------------------------------'