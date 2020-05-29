import base64
import json
import requests

OPENALPR_CLOUD_SECRET_KEY = 'sk_013361c164cbbedb0b82f609'

def cloudAPI():
    # Sample image file is available at http://plates.openalpr.com/ea7the.jpg
    IMAGE_PATH = 'frame.png'

    with open(IMAGE_PATH, 'rb') as image_file:
        img_base64 = base64.b64encode(image_file.read())

    url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=nz&secret_key=%s' % (OPENALPR_CLOUD_SECRET_KEY)
    r = requests.post(url, data=img_base64)
    json_result = r.json()
    # print(json.dumps(r.json(), indent=2))
    print(json_result['img_width'])
    print(json_result['results'])
    print(json_result['results'][0]['plate'])
    print(json_result['results'][0]['coordinates'])

if __name__ == '__main__':
    cloudAPI()