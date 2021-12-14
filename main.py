from whatsapp_helper import WhatsAppHelper

wap = WhatsAppHelper()


def get_main_data(email):

    print(email)
    # acc_id = wap.create_member(email)
    acc_id = 39
    print(acc_id)

    api_id, api_token = wap.get_new_chat(email, acc_id)
    print(api_id, api_token)

    return acc_id, api_id, api_token


def start(email):

    acc_id, api_id, api_token = get_main_data(email)

    qr_path = wap.get_qr_from_status(acc_id, api_id, api_token)

    input(f'Отсканируйте qr по пути: {qr_path}')

    wap_info = wap.check_whatsapp_info(acc_id, api_id, api_token)
    print(wap_info)


if __name__ == '__main__':

    # ввести сюда email для регистрации аккаунта
    email_o = 'temp@gmail.com'

    qr_path = wap.get_qr_from_status(39, 21, 'PAjaZ747B-uQHpG9')
    print(qr_path)

    start(email_o)
