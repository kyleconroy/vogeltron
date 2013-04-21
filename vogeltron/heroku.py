import requests
import json


def url(uri):
    return 'https://api.heroku.com' + uri


def jsonify(func):
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        resp.raise_for_status()
        return resp.json()
    return wrapper


class Client(object):

    def __init__(self, api_key):
        self.s = requests.Session()
        self.s.auth = ('', api_key)
        self.s.headers.update({'Accept': 'application/json'})

    def get_app(self, name):
        resp = self.s.get(url('/apps/' + name))

        if not resp.ok:
            return None

        return resp.json()

    @jsonify
    def create_app(self, name):
        return self.s.post(url('/apps/'), data={'app[name]': name})

    @jsonify
    def get_config(self, name):
        return self.s.get(url('/apps/' + name + '/config_vars'))

    @jsonify
    def set_config(self, name, config_vars):
        return self.s.put(url('/apps/' + name + '/config_vars'),
                          data=json.dumps(config_vars))

    def install_addon(self, name, addon):
        resp = self.s.post(url('/apps/' + name + '/addons/' + addon))
        if resp.status_code == 422:
            return
        resp.raise_for_status()
