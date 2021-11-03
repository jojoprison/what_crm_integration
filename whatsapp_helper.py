import json
import time
from base64 import decodebytes

import requests as requests

from db import DB
import time_converter


class WhatsAppHelper:
    # what_crm
    task_api_url = 'https://dev.whatsapp.sipteco.ru/v3/'
    # chat-api
    api_url_pad = 'https://api.chat-api.com/'

    headers = {'X-Whatsapp-Token': '5d8af8faaeb61680883a850be0c577e2',
               'Content-type': 'application/json'}

    db = DB()

    def create_member(self, email):

        acc_id = self.db.get_working_acc_id_by_email(email)

        if not acc_id:

            reg_user_post = 'https://dev.whatsapp.sipteco.ru/v3/integrations/install?crm=LK'
            content = {
                'domain': email
            }

            req = requests.post(reg_user_post, headers=self.headers, data=json.dumps(content))

            member = req.json()
            print(member)
            acc_id = member['id']
            date_create = time_converter.unix_to_msc(member['date_add'])
            date_trial = time_converter.unix_to_msc(member['date_trial'])

            self.db.add_member(acc_id, email, date_create, date_trial)

        return acc_id

    def get_new_chat(self, email, acc_id):
        # метод получения нового чата
        # отсюда получаем ID, TOKEN
        get_new_chat_url = f'{self.task_api_url}chat/spare?crm=LK&domain={email}'

        req = requests.get(get_new_chat_url, headers=self.headers)

        chat = req.json()
        api_id = chat['id']
        api_token = chat['token']
        instance_id = chat['instanceId']

        self.db.add_chat_to_member(acc_id, email, api_id, api_token, instance_id)

        return api_id, api_token

    def chat_interaction(self, api_id, api_token, method_name, method_type, content=None,
                         what_crm_dev=True, insert_token=True, init_status=False):

        # метод для работы с чатом
        # пример https://dev.whatsapp.sipteco.ru/v3/instance23/me?token=123DYUUD
        if what_crm_dev:
            chat_interaction_url = f'{self.task_api_url}instance{api_id}/{method_name}'
        else:
            chat_interaction_url = f'{self.api_url_pad}instance{api_id}/{method_name}'

        if insert_token:
            chat_interaction_url += f'?token={api_token}'

        if init_status:
            chat_interaction_url += '&full=1'

        if method_type == 'POST':
            resp = requests.post(chat_interaction_url, headers=self.headers,
                                data=json.dumps(content))
        elif method_type == 'GET':
            resp = requests.get(chat_interaction_url, headers=self.headers)
        else:
            return 'not GET or POST...'

        return resp.json()

    def get_qr_code(self, api_id, api_token, what_crm_dev=True):

        if what_crm_dev:
            get_qr_url = f'{self.task_api_url}instance{api_id}/qr_code?token={api_token}'
        else:
            get_qr_url = f'{self.api_url_pad}instance{api_id}/qr_code?token={api_token}'

        qr_code = requests.get(get_qr_url, headers=self.headers)

        return qr_code

    def download_qr_code(self, acc_id, api_id):

        qr_path = f'qr_{api_id}.png'

        qr_base64 = self.db.get_qr(acc_id, api_id)
        # переводим в байты
        qr_base64_converted = qr_base64.encode('utf-8')

        # пишем байты, поэтому wb
        with open(qr_path, 'wb') as f:
            # декодируем байты и пишем в файл
            f.write(decodebytes(qr_base64_converted))

        return qr_path

    def get_qr_from_status(self, acc_id, api_id, api_token, what_crm_dev=True):

        # предварительно делаем ребут аккаунта
        print(self.chat_interaction(api_id, api_token, 'reboot', 'GET', insert_token=True))

        status = self.chat_interaction(api_id, api_token, 'status', 'GET',
                                       what_crm_dev=what_crm_dev)
        print(status)

        # каждые 30 секунд после ребута запрашиваем статус и ждем, когда получим qr
        while not status.get('qrCode'):
            time.sleep(30)

            status = self.chat_interaction(api_id, api_token, 'status', 'GET',
                                           init_status=True)
            print(status)

        # сохраняем qr в бд
        self.db.save_qr(acc_id, api_id, status['qrCode'])

        # скачиваем qr в корень проекта
        qr_path = self.download_qr_code(acc_id, api_id)
        print(qr_path, ' downloaded')

        return qr_path

    # получаем информацию о номере и имени аккаунта whatsapp
    def check_whatsapp_info(self, acc_id, api_id, api_token):

        me_info = self.chat_interaction(api_id, api_token, 'me', 'GET')
        print(me_info)

        if me_info.get('name'):

            phone = 'не определен' if me_info['id'] == 'undefined' else me_info['id']
            name = me_info['name']

            if self.db.update_whatsapp_info(acc_id, api_id, phone, name):
                print(f'whatsapp информация юзера {acc_id} с API {api_id} обновлена')
            else:
                print(f'неудача обновления whatsapp инфы юзера {acc_id} с API {api_id}')

            phone_to = '79872745052'

            send_msg_res = self.send_msg(api_id, api_token, phone, name, phone_to)

            return send_msg_res
        else:
            return 'Аккаунт не авторизирован'

    def send_msg(self, api_id, api_token, phone_from, name, phone_to, what_crm_dev=True):

        content = {
            "body": f"Сообщение отправлено через chat-api.com\n\nНомер телефона: {phone_from}\nИмя: {name}",
            "phone": phone_to
        }

        res = self.chat_interaction(api_id, api_token, 'sendMessage', 'POST',
                                    content, what_crm_dev)

        if res['sent'] == 'true':
            return f'сообщение отправлено от {phone_from} {name}'
        else:
            return f'сообщение не доставлено от {phone_from} {name}'


if __name__ == '__main__':
    wap = WhatsAppHelper()

    wap.download_qr_code(39, 20)

    # post_res = wap.create_member(email)
    # post_res = {'id': 22, 'date_add': 1635091232, 'date_trial': 1635350432, 'is_premium': 0}
    # print(post_res)

    # chat = wap.get_new_chat(email)
    # chat = {'id': 2, 'token': 'NTajeKzXU8onSmF5', 'instanceId': '2a01:4f9:c011:4f7c:3::17'}
    # print(chat)
