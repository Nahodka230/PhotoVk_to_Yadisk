import datetime
from datetime import datetime

import requests
import yadisk
import json
from tqdm import tqdm


class VK:

   def __init__(self, access_token):
       self.token = access_token

   def get_photos(self, album_id,  user_id, count=5):
       url = 'https://api.vk.com/method/photos.get'
       params = {
           'access_token': self.token,
           'owner_id': user_id,
           'album_id': album_id,
           'photo_sizes': '1',
           'count': count,
           'v': '5.131',
           'extended': '1',
           'rev':'1'
        }
       response = requests.get(url, params = params)
       datatoya = []
       datatojson = []
       likes = []

       if response.ok:
           data = response.json()['response']['items']

           for photo in data:
               likes.append(photo['likes']['count'])

           for photo in data:
               sizes = photo['sizes']

               max_size = max(sizes, key=lambda s: s['width'] * s['height'])
               if likes.count(photo['likes']['count']) > 1:
                   date = datetime.fromtimestamp(photo['date'])
                   photo_name = f"{photo['likes']['count']} {date}.jpg"
               else:
                   photo_name = f"{photo['likes']['count']}.jpg"
               datatoya.append({'photo_url': max_size['url'], 'size': max_size['type'],'name':photo_name})
               datatojson.append({"file_name": photo_name, "size":max_size['type']})
           with open('data.json', 'w') as f:
               json.dump(datatojson, f)
           return datatoya
       else:
           print('Ошибка:', response.status_code)
class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def upload(self, folder_name, info_by_photo):
        create_folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Authorization': f'OAuth {self.token}'}
        params = {'path': f'/{folder_name}'}
        YandexDisk = yadisk.YaDisk(token=self.token)

        if YandexDisk.exists('Фото из ВК') == False:
            response = requests.put(create_folder_url, headers=headers, params=params)
            response.raise_for_status()
        url = f'https://cloud-api.yandex.net/v1/disk/resources/upload/'
        for photo in tqdm(info_by_photo, desc='Processing photos', unit='photo'):
            response = requests.post(url=url, headers=headers, params={'path': f"/{folder_name}/{photo['name']}",'overwrite': 'true', 'url': photo['photo_url']})

        # Проверка успешности запроса
        if response.ok:
            print('Файлы успешно сохранены на Яндекс.Диск')
        else:
            print(f'Ошибка {response.status_code}: {response.reason}')



if __name__ == '__main__':

    ya_token = input('Введите токен с Полигона Яндекс.Диска: ')
    uploader = YaUploader(ya_token)

    with open('token1.txt', 'r') as file_object:
        vk_token = file_object.read().strip()
    user_id = input('Введите id пользователя vk: ')
    #'id132231432'
    vk = VK(vk_token)
    dict_info = vk.get_photos('profile', user_id)
    folder_name = 'Фото из ВК'
    uploader.upload(folder_name,dict_info)

