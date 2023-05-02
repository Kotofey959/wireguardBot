import sqlite3
import time


def my_factory(c, r):
    d = {}
    for i, name in enumerate(c.description):
        d[name[0]] = r[i]  # Ключи в виде названий полей
        d[i] = r[i]
    return d


conn = sqlite3.connect("E:\\PyCharm Community Edition 2022.3\\wireguardBot\\bot_main\\wireguardBot\\vpn_data.db",
                       check_same_thread=False)
conn.row_factory = my_factory
cursor = conn.cursor()


def add_or_update_user(chat_id: int, amount: int = 0):
    statement = "INSERT INTO account (id, amount) " \
                "VALUES (:id, :amount)"
    try:
        cursor.execute(statement, {
            "id": chat_id,
            "amount": amount,
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    else:
        cursor.connection.commit()


def get_account_by_chat_id(chat_id: int):
    statement = "SELECT * FROM account WHERE id = :chat_id"

    try:
        cursor.execute(statement, {
            "chat_id": chat_id,
        })
        arr = cursor.fetchone()
        print(arr)
        if arr is None:
            return False
        return arr
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    return False


def insert_or_update(chat_id: int, account, amount: int = 0):
    id_tg = chat_id
    id_vpn = account['id']
    private_key = account['private_key']
    public_key = account['public_key']
    preshared_key = account['preshared_key']
    name = account['name']
    allocated_ips = account['allocated_ips'][0]
    allowed_ips = account['allowed_ips'][0]
    extra_allowed_ips = "" if len(account['extra_allowed_ips']) == 0 else account['extra_allowed_ips'][0]
    use_server_dns = account['use_server_dns']
    enabled = account['enabled']
    created_at = account['created_at']
    statement = "INSERT INTO users (id_tg, id_vpn, private_key, public_key, preshared_key, name, allocated_ips, " \
                "allowed_ips, extra_allowed_ips, use_server_dns, enabled, created_at, amount) " \
                "VALUES (:id_tg, :id_vpn, :private_key, :public_key, :preshared_key, :name, :allocated_ips, " \
                ":allowed_ips, :extra_allowed_ips, :use_server_dns, :enabled, :created_at, :amount)"

    try:
        cursor.execute(statement, {
            "id_tg": id_tg,
            "id_vpn": id_vpn,
            "private_key": private_key,
            "public_key": public_key,
            "preshared_key": preshared_key,
            "name": name,
            "allocated_ips": allocated_ips,
            "allowed_ips": allowed_ips,
            "extra_allowed_ips": extra_allowed_ips,
            "use_server_dns": 1 if use_server_dns is True else 0,
            "enabled": 1 if enabled is True else 0,
            "created_at": created_at,
            "amount": amount,
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    else:
        cursor.connection.commit()


def get_all_users():
    statement = "SELECT * FROM users"

    try:
        cursor.execute(statement)
        arr = cursor.fetchall()
        if arr is None:
            return False
        return arr
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    return False


def update_amount(chat_id: int,
                  amount: int):
    statement = "UPDATE account SET amount = :amount WHERE id = :user_id"
    try:
        cursor.execute(statement, {
            "user_id": chat_id,
            "amount": amount
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    else:
        cursor.connection.commit()


def update_amount_vpn(id: int,
                      amount: int):
    statement = "UPDATE users SET amount = :amount WHERE id = :user_id"
    try:
        cursor.execute(statement, {
            "user_id": id,
            "amount": amount
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    else:
        cursor.connection.commit()


def update_enable_status(
        chat_id: int,
        enabled: int):
    statement = "UPDATE users SET enabled = :enabled WHERE id = :user_id"
    try:
        cursor.execute(statement, {
            "user_id": chat_id,
            "enabled": enabled
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    else:
        cursor.connection.commit()


def get_vpn_by_chat_id(chat_id: int):
    statement = "SELECT * FROM users WHERE id_tg = :chat_id"

    try:
        cursor.execute(statement, {
            "chat_id": chat_id,
        })
        arr = cursor.fetchall()
        if len(arr) == 0:
            return False
        return arr
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    return False


def get_vpn_by_vpn_id(id_vpn: str):
    statement = "SELECT * FROM users WHERE id_vpn = :id_vpn"

    try:
        cursor.execute(statement, {
            "id_vpn": id_vpn,
        })
        arr = cursor.fetchone()
        if arr is None:
            return False
        return arr
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    return False


def add_payment(user_id: int, value_to_pay: int, label: str):
    statement = "UPDATE account SET value_to_pay = :value_to_pay, label = :label, is_paid = " \
                ":is_paid WHERE id = :user_id"
    try:
        cursor.execute(statement, {
            "user_id": user_id,
            "value_to_pay": value_to_pay,
            "label": label,
            "is_paid": 0
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    else:
        cursor.connection.commit()


def update_payment_status(user_id: int, status: int, amount: int):
    statement = "UPDATE account SET is_paid = :status, amount = :amount WHERE id = :user_id"
    try:
        cursor.execute(statement, {
            "user_id": user_id,
            "status": status,
            "amount": amount
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    else:
        cursor.connection.commit()


def get_payment_status(user_id: int):
    statement = "SELECT * FROM users WHERE id = :user_id"
    try:
        cursor.execute(statement, {
            "user_id": user_id
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
        arr = cursor.fetchone()
        if arr is None:
            return False
        return arr
    return False


def add_payment_in_history(user_id: int,
                           amount: int,
                           label: str):
    statement = "INSERT INTO history (user_id, date, amount, label) " \
                "VALUES (:user_id, :date, :amount, :label)"
    date = time.strftime("%y.%m.%d %H:%M")
    try:
        cursor.execute(statement, {
            "user_id": user_id,
            "date": date,
            "amount": amount,
            "label": label,
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    else:
        cursor.connection.commit()


def update_amount_vpn_id(vpn_id: str,
                         amount: int):
    statement = "UPDATE users SET amount = :amount WHERE id_vpn = :vpn_id"
    try:
        cursor.execute(statement, {
            "vpn_id": vpn_id,
            "amount": amount
        })
    except sqlite3.DataError as err:
        print("Ошибка: ", err)
    else:
        cursor.connection.commit()

