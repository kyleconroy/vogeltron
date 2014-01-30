import requests
import time
import logging

HEADERS = {'User-Agent': "/r/SFGiants Sidebar Bot"}

logger = logging.getLogger('vogelton')


# Try a request 3 times, with a 1 second wait in between failures
def _retry(session, method, *args, **kwargs):
    for i in range(5):
        try:
            resp = session.request(method, *args, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            if i >= 4:
                raise e
            else:
                logger.warn('Retrying {} to {}'.format(method, args))
                time.sleep(1)


class Client(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password

        payload = {'user': self.username, 'passwd': self.password}

        resp = self.post('https://ssl.reddit.com/api/login',
                         data=payload, headers=HEADERS)

        self.s = requests.Session()
        self.s.cookies = resp.cookies
        self.s.headers.update(HEADERS)

        resp = self.get('http://www.reddit.com/api/me.json')
        resp.raise_for_status()

        self.user_hash = resp.json()['data']['modhash']

    def get(self, *args, **kwargs):
        return _retry(getattr(self, 's', requests), 'GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return _retry(getattr(self, 's', requests), 'POST', *args, **kwargs)

    def _user_where(self, user, where):
        url = "http://www.reddit.com/user/{}/{}.json".format(user, where)
        resp = self.get(url)
        return resp.json()['data']['children']

    def submitted(self, user):
        return self._user_where(user, 'submitted')

    def about(self, subreddit):
        url = "http://www.reddit.com/r/{}/about.json".format(subreddit)
        resp = self.get(url)
        return resp.json()['data']

    def settings(self, subreddit):
        url = "http://www.reddit.com/r/{}/about/edit/.json".format(subreddit)
        resp = self.get(url)
        return resp.json()['data']

    def admin(self, subreddit, data):
        data['uh'] = self.user_hash

        resp = self.post("http://www.reddit.com/api/site_admin", data=data)

        return resp.json()

    def sticky(self, postid):
        payload = {
            'id': postid,
            'state': True,
            'uh': self.user_hash,
        }

        resp = self.post('http://www.reddit.com/api/set_subreddit_sticky',
                         data=payload)
        return resp.json()

    def submit(self, subreddit, title, text):
        payload = {
            'kind': 'self',
            'sr': subreddit,
            'title': title,
            'text': text,
            'uh': self.user_hash,
        }

        resp = self.post('http://www.reddit.com/api/submit', data=payload)
        return resp.json()

    def edit(self, post_id, body):
        payload = {
            'thing_id': post_id,
            'text': body,
            'uh': self.user_hash,
        }

        resp = self.post('http://www.reddit.com/api/editusertext',
                         data=payload)
        return resp.json()
