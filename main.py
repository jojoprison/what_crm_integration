from whatsapp_helper import WhatsAppHelper

wap = WhatsAppHelper()


def get_main_data(email):
    acc_id = wap.create_member(email)
    print(acc_id)

    api_id, api_token = wap.get_new_chat(email, acc_id)
    print(api_id, api_token)

    return acc_id, api_id, api_token


def start(email):

    acc_id, api_id, api_token = get_main_data(email)

    wap.get_qr_from_status(api_id, api_token)

    wap_info = wap.check_whatsapp_info(acc_id, api_id, api_token)
    print(wap_info)


if __name__ == '__main__':

    # email = 'egyabig2@gmail.com'
    # ввести сюда email для регистрации аккаунта
    email = ''
    start(email)
