import requests

HEADERS = {'User-Agent': "/r/SFGiants Sidebar Bot"}


class Client(object):

    def __init__(self, user_agent):
        self.user_agent = user_agent

    def _authenticate(self, auth):
        username, password = auth
        payload = {'user': username, 'passwd': password}

        resp = requests.post('https://ssl.reddit.com/api/login',
                             data=payload, headers=HEADERS)
        resp.raise_for_status()

        return resp.cookies

    def submit(self, subreddit, title, text='', auth=None):
        cookies = self._authenticate(auth)

        resp = requests.get('http://www.reddit.com/api/me.json',
                            cookies=cookies, headers=HEADERS)
        resp.raise_for_status()

        payload = {
            'kind': 'self',
            'sr': subreddit,
            'title': title,
            'text': text,
            'uh': resp.json()['data']['modhash'],
        }

        resp = requests.post('http://www.reddit.com/api/submit',
                             headers=HEADERS, data=payload, cookies=cookies)
        resp.raise_for_status()

        return resp
