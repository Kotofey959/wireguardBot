import requests
import pickle

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

PASSWORD = 'admin'
USERNAME = 'admin'
URL = 'http://212.118.43.83:5000/'


def login(session: requests.Session) -> bool:
    payload = {
        'password': PASSWORD,
        'username': USERNAME,
    }
    url = URL + 'login'
    r = session.post(url, headers=headers, json=payload)
    with open('cookie', 'wb') as f:
        pickle.dump(session.cookies, f)
    return r.json()['status']


def add_client(name: str):
    session = requests.session()
    url = URL + 'new-client'
    print(url)
    with open('cookie', 'rb') as f:
        session.cookies.update(pickle.load(f))
    allocated_ips = suggest_client_ips(session)
    payload = {
        'allocated_ips': allocated_ips,
        'allowed_ips': ["0.0.0.0/0"],
        'email': "",
        'enabled': True,
        'extra_allowed_ips': [],
        'name': name,
        'preshared_key': "",
        'public_key': "",
        'use_server_dns': True
    }
    r = session.post(url=url, headers=headers, json=payload)
    try:
        print(r.json())
        apply_wg_config()
        return r.json()
    except Exception as ex:
        print(ex)
        login_status = login(session)
        if not login_status:
            return False
    r = session.post(url=url, headers=headers, json=payload)
    apply_wg_config()
    print(r.json())
    return r.json()


def set_client_status(user_id: str, status: bool) -> bool:
    session = requests.session()
    url = URL + 'client/set-status'
    with open('cookie', 'rb') as f:
        session.cookies.update(pickle.load(f))
    payload = {
        'id': user_id,
        'status': status,
    }
    r = session.post(url=url, headers=headers, json=payload)
    try:
        print(r.json())
        apply_wg_config()
        return r.json()["status"]
    except Exception as ex:
        print(ex)
        login_status = login(session)
        if not login_status:
            return False
    r = session.post(url=url, headers=headers, json=payload)
    apply_wg_config()
    return r.json()["status"]


def remove_client(user_id: str) -> bool:
    session = requests.session()
    url = URL + 'remove-client'
    with open('cookie', 'rb') as f:
        session.cookies.update(pickle.load(f))
    payload = {
        'id': user_id
    }
    r = session.post(url=url, headers=headers, json=payload)
    try:
        print(r.json())
        apply_wg_config()
        return r.json()["status"]
    except Exception as ex:
        print(ex)
        login_status = login(session)
        if not login_status:
            return False
    r = session.post(url=url, headers=headers, json=payload)
    apply_wg_config()
    return r.json()["status"]


def download_client(client_id: str) -> bytes | int:
    session = requests.session()
    url = URL + 'download'
    with open('cookie', 'rb') as f:
        session.cookies.update(pickle.load(f))
    data = {
        'clientid': client_id
    }
    r = session.get(url=url, headers=headers, params=data)
    if 'text/html' not in r.headers['content-type']:
        return r.content
    login_status = login(session)
    if not login_status:
        return 0
    r = session.get(url=url, headers=headers, params=data)
    return r.content


def get_all_clients():
    session = requests.session()
    url = URL + 'api/clients'
    with open('cookie', 'rb') as f:
        session.cookies.update(pickle.load(f))
    r = session.get(url=url, headers=headers)
    try:
        return r.json()
    except Exception as ex:
        print(ex)
        login_status = login(session)
        if not login_status:
            return False
    r = session.get(url=url, headers=headers)
    return r.json()


def get_client_by_id(client_id: str):
    session = requests.session()
    url = URL + f'api/client/{client_id}'
    with open('cookie', 'rb') as f:
        session.cookies.update(pickle.load(f))
    r = session.get(url=url, headers=headers)
    try:
        return r.json()
    except Exception as ex:
        print(ex)
        login_status = login(session)
        if not login_status:
            return 0
    r = session.get(url=url, headers=headers)
    return r.json()


def suggest_client_ips(session: requests.Session):
    url = URL + 'api/suggest-client-ips'
    with open('cookie', 'rb') as f:
        session.cookies.update(pickle.load(f))
    r = session.get(url=url, headers=headers)
    try:
        return r.json()
    except Exception as ex:
        print(ex)
        login_status = login(session)
        if not login_status:
            return 0
    r = session.get(url=url, headers=headers)
    print(r.text)
    return r.json()


def apply_wg_config() -> bool:
    session = requests.session()
    headers_wg_config = headers
    headers_wg_config['x-requested-with'] = 'XMLHttpRequest'
    headers_wg_config['accept'] = 'application/json, text/javascript, */*; q=0.01'
    headers_wg_config['content-type'] = 'application/json'
    url = URL + 'api/apply-wg-config'
    with open('cookie', 'rb') as f:
        session.cookies.update(pickle.load(f))
    r = session.post(url=url, headers=headers_wg_config)
    print(r.text)
    try:
        print("apply config:", r.json())
        return r.json()["status"]
    except Exception as ex:
        print(ex)
        login_status = login(session)
        if not login_status:
            return False
    r = session.post(url=url, headers=headers)
    print("apply config:", r.json())
    return r.json()["status"]
