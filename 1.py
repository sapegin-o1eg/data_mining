# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests


class GithubUserRepos:
    user_agent = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/74.0.3729.169 Safari/537.36"""

    def __init__(self, username):
        self.username = username
        self.filename = f'{self.username}.json'
        self.url = f'https://api.github.com/users/{self.username}/repos'

    def get(self):
        response = requests.get(self.url, headers={'User-Agent': self.user_agent})
        with open(self.filename, 'w') as outfile:
            print(response.text, file=outfile)


if __name__ == '__main__':
    repos = GithubUserRepos('sapegin-o1eg')
    repos.get()
