import requests

HEADERS = {'User-Agent': "/r/SFGiants Sidebar Bot"}


class Client(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password

        payload = {'user': self.username, 'passwd': self.password}

        resp = requests.post('https://ssl.reddit.com/api/login',
                             data=payload, headers=HEADERS)
        resp.raise_for_status()

        self.s = requests.Session()
        self.s.cookies = resp.cookies
        self.s.headers.update(HEADERS)

        resp = self.s.get('http://www.reddit.com/api/me.json')
        resp.raise_for_status()

        self.user_hash = resp.json()['data']['modhash']

    def _user_where(self, user, where):
        url = "http://www.reddit.com/user/{}/{}.json".format(user, where)
        resp = self.s.get(url)
        resp.raise_for_status()
        return resp.json()['data']['children']

    def submitted(self, user):
        return self._user_where(user, 'submitted')

    def about(self, subreddit):
        url = "http://www.reddit.com/r/{}/about.json".format(subreddit)
        resp = self.s.get(url)
        resp.raise_for_status()
        return resp.json()['data']

    def settings(self, subreddit):
        url = "http://www.reddit.com/r/{}/about/edit/.json".format(subreddit)
        resp = self.s.get(url)
        resp.raise_for_status()
        return resp.json()['data']

    def admin(self, subreddit, data):
        data['uh'] = self.user_hash

        resp = self.s.post("http://www.reddit.com/api/site_admin", data=data)
        resp.raise_for_status()

        return resp.json()

    def sticky(self, postid):
        payload = {
            'id': postid,
            'state': True,
            'uh': self.user_hash,
        }

        resp = self.s.post('http://www.reddit.com/api/set_subreddit_sticky',
                           data=payload)
        resp.raise_for_status()
        return resp.json()

    def submit(self, subreddit, title, text):
        payload = {
            'kind': 'self',
            'sr': subreddit,
            'title': title,
            'text': text,
            'uh': self.user_hash,
        }

        resp = self.s.post('http://www.reddit.com/api/submit', data=payload)
        resp.raise_for_status()
        return resp.json()

    def edit(self, post_id, body):
        payload = {
            'thing_id': post_id,
            'text': body,
            'uh': self.user_hash,
        }

        resp = self.s.post('http://www.reddit.com/api/editusertext',
                           data=payload)
        resp.raise_for_status()
        return resp.json()
