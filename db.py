import sqlite3

import time_converter


class DB:
    __conn = None

    # синглтон, lazy init, будем юзать sqlite, для тестового задания подходит
    def get_conn(self):
        if not self.__conn:
            self.__conn = sqlite3.connect('phones.db')
        return self.__conn

    # закрываем коннект к базе деструктором
    def __del__(self):
        if self.__conn:
            self.__conn.close()

    # создаем бд для телефонов
    def create_db(self):
        conn = self.get_conn()

        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS phones (
            account_id INTEGER NOT NULL, 
            email TEXT,
            date_create TEXT, 
            date_trial TEXT,
            api_id INTEGER,
            api_token TEXT,
            instance_id TEXT,
            qr_base64 TEXT,
            phone INTEGER,
            name TEXT
            );''')

        conn.commit()

        return True

    # общий метод добавления участника
    def add_member(self, account_id, email=None, date_create=None, date_trial=None, api_id=None,
                   api_token=None, instance_id=None, qr_base64=None, phone=None, name=None):

        query = 'INSERT INTO phones(account_id, email, date_create, date_trial'
        values = [account_id, email, date_create, date_trial]

        # слайсим, чтоб выдернуть только необязательные аргументы метода
        args = list(locals().items())[5:-2]

        # бегаем по аргументам метода, формируем запрос
        for arg in args:

            if arg[1]:
                query += f', {arg[0]}'
                values.append(arg[1])

        for idx, val in enumerate(values):
            if type(val) == str:
                values[idx] = f'"{val}"'
            else:
                values[idx] = str(val)

        # добавляем значения в запрос
        query += f') VALUES({", ".join(values)});'

        print(query)

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()

        return True

    def add_chat_to_member(self, acc_id, email, api_id, api_token, instance_id):

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(f"SELECT account_id, api_id, date_create, date_trial FROM phones "
                    f"WHERE account_id = {acc_id}")

        accs = cur.fetchall()

        empty_acc_exist = False

        for acc in accs:
            if not acc[1]:
                empty_acc_exist = True
                break

        if empty_acc_exist:

            query = f"UPDATE phones SET api_id = {api_id}, api_token = '{api_token}', " \
                    f"instance_id = '{instance_id}' WHERE account_id = {acc_id} and " \
                    f"ifnull(api_id, '') = '';"

            print(query)

            conn = self.get_conn()
            cur = conn.cursor()

            cur.execute(query)

            conn.commit()
        else:

            date_create = ''
            date_trial = ''

            for acc in accs:
                if acc[0] == acc_id:
                    date_create = acc[2]
                    date_trial = acc[3]

            self.add_member(acc_id, email=email, date_create=date_create,
                            date_trial=date_trial, api_id=api_id, api_token=api_token,
                            instance_id=instance_id)

        return True

    def save_qr(self, acc_id, api_id, qr_base64):

        # т.к. знаем сигнатуру src, разделим данной последовательностью на 2 части
        # после запятой будет искомая последовательность байтов QR кода
        qr_base64_converted = qr_base64.split('base64,')[1]

        # кодируем строку в последовательность байтов
        # TODO поставить, если будут проблемы с сохранением
        # qr_base64_converted = qr_base64_converted.encode('utf-8')

        query = f'UPDATE phones SET qr_base64 = "{qr_base64_converted}" WHERE ' \
                f'account_id = {acc_id} and api_id = {api_id};'

        print(query)

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()

        return True

    def update_whatsapp_info(self, acc_id, api_id, phone, name):
        query = f'UPDATE phones SET phone = {phone}, name = {name} ' \
                f'WHERE account_id = {acc_id} and api_id = {api_id};'

        print(query)

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()

        return True

    def get_qr(self, acc_id, api_id):

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(f'SELECT qr_base64 FROM phones '
                    f'WHERE account_id = {acc_id} and api_id = {api_id}')

        result = cur.fetchone()[0]

        return result

    def get_working_acc_id_by_email(self, email):

        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute(f"SELECT date_trial, account_id FROM phones WHERE email = '{email}'")
        # cur.execute("SELECT date_trial, account_id FROM phones WHERE email = ?", email)

        acc_expiration_dates = cur.fetchall()

        for expiration_date in acc_expiration_dates:
            if not time_converter.has_passed(expiration_date[0]):
                return expiration_date[1]

        return None


if __name__ == '__main__':
    db = DB()
    db.get_conn()
    # db.create_db()

    # db.add_member(1, 's', 's', instance_id='123', api_id=1)

    # db.save_qr(22, 16, 'data:image/png;base64,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')

    # qr = db.get_qr(22, 16)
    # print(qr)

    # god = db.add_chat_to_member(22, 666, 'ada', 'asda')
    # print(god)

    # w_acc_id = db.get_working_acc_id()
    # print(w_acc_id)

    # email = 'temp2@gmail.com'
    # print(db.get_working_acc_id_by_email(email))

    btt = 'iVBORw0KGgoAAAANSUhEUgAAAOQAAADkCAYAAACIV4i'
    conv = btt.encode('utf-8')
    print(conv.decode('utf-8'))
    print(type(conv))

