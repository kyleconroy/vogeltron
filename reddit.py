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

    def about(self, subreddit):
        url = "http://www.reddit.com/r/{}/about/edit/.json".format(subreddit)
        resp = self.s.get(url)
        resp.raise_for_status()
        return resp.json()['data']

    def update_about(self, subreddit, data):
        data['uh'] = self.user_hash

        resp = self.s.post("http://www.reddit.com/api/site_admin", data=data)
        resp.raise_for_status()

        return resp.json()

    def submit(self, subreddit, title, text=''):
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
