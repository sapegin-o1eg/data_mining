import requests
from bs4 import BeautifulSoup
import time
import random
from pymongo import MongoClient
import urllib
import re


class JobsParser:
    USER_AGENT = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/74.0.3729.169 Safari/537.36"""

    def __init__(self, verbose=None):
        self.superjob_base = 'https://www.superjob.ru'
        self.superjob_url = '/vacancy/search/'
        self.superjob_params = {'keywords': None,
                                'geo[t][0]': 25}
        self.hh_base = 'https://hh.ru'
        self.hh_url = '/search/vacancy'
        self.hh_params = {'area': 53,
                          'st': 'searchVacancy',
                          'text': None}
        self.verbose = verbose

    def superjob_job_parse(self, job):
        salary_from = salary_to = None
        job_re = re.compile('^_\S{5} \S{5} \S{5} _\S{5} _\S{5}$')
        url_re = re.compile('^\S{5} _\S{5}.*_\S{5} _\S{5}$')
        title = job.find('div', attrs={'class': job_re}).text
        job_url = job.find('a', {'class': url_re}).attrs['href']
        salary = job.find('span', {'class': re.compile('^_\S{5} _\S{5}.* \S{5} _\S{5} _\S{5}$')}).text
        salary = re.sub('[\xa0₽]', '', salary).split('—')
        from_re = re.compile('^от', re.IGNORECASE)
        to_re = re.compile('^до', re.IGNORECASE)

        if len(salary) == 2:
            salary_from = salary[0]
            salary_to = salary[1]
        elif re.search(from_re, salary[0]):
            salary_from = re.sub(from_re, '', salary[0])
        elif re.search(to_re, salary[0]):
            salary_to = re.sub(to_re, '', salary[0])
        else:
            salary_from = salary_to = salary[0]

        result = {'title': title,
                  'job_url': f'{self.superjob_base}{job_url}',
                  'salary_from': salary_from,
                  'salary_to': salary_to,
                  'source': 'superjob.ru'}
        return result

    def superjob_parse(self, keyword=None, url=None):
        if not url:
            self.superjob_params['keywords'] = keyword
            params = urllib.parse.urlencode(self.superjob_params)
            url = f'{self.superjob_base}{self.superjob_url}?{params}'

        time.sleep(random.randint(1, 3))
        response = requests.get(url, headers={'User-Agent': self.USER_AGENT})
        soup = BeautifulSoup(response.text, 'lxml')
        body = soup.html.body
        jobs_re = re.compile('^_\S{5} _\S{5} \S{5} _\S{5}$')
        jobs = body.findAll('div', attrs={'class': jobs_re})

        client = MongoClient('localhost', 27017)
        database = client.lesson2
        collection = database.jobs

        for job in jobs:
            result = self.superjob_job_parse(job)
            if self.verbose:
                print(result)
            collection.insert_one(result)

        try:
            url = body.find('a', attrs={'class': 'f-test-link-dalshe'}).attrs['href']
        except AttributeError:
            url = None

        if url:
            self.superjob_parse(url=f'{self.superjob_base}{url}')

    def hh_job_parse(self, job):
        salary_from = salary_to = None
        title = job.find('div', attrs={'class': 'resume-search-item__name'}).text
        job_url = job.find('a', attrs={'class': 'bloko-link'}).attrs['href']
        try:
            salary = job.find('div', attrs={'class': 'vacancy-serp-item__compensation'}).text
            salary = re.sub('[\s]|руб.', '', salary).split('-')
            from_re = re.compile('^от', re.IGNORECASE)
            to_re = re.compile('^до', re.IGNORECASE)
            if len(salary) == 2:
                salary_from = salary[0]
                salary_to = salary[1]
            elif re.search(from_re, salary[0]):
                salary_from = re.sub(from_re, '', salary[0])
            elif re.search(to_re, salary[0]):
                salary_to = re.sub(to_re, '', salary[0])
            else:
                salary_from = salary_to = salary[0]
        except AttributeError:
            salary_from = None
            salary_to = None

        result = {'title': title,
                  'job_url': job_url,
                  'salary_from': salary_from,
                  'salary_to': salary_to,
                  'source': 'hh.ru'}
        return result

    def hh_parse(self, keyword=None, url=None):
        if not url:
            self.hh_params['text'] = keyword
            params = urllib.parse.urlencode(self.hh_params)
            url = f'{self.hh_base}{self.hh_url}?{params}'

        time.sleep(random.randint(1, 3))
        response = requests.get(url, headers={'User-Agent': self.USER_AGENT})
        soup = BeautifulSoup(response.text, 'lxml')
        body = soup.html.body
        jobs = body.findAll('div', attrs={'class': 'vacancy-serp-item'})

        client = MongoClient('localhost', 27017)
        database = client.lesson2
        collection = database.jobs

        for job in jobs:
            result = self.hh_job_parse(job)
            if self.verbose:
                print(result)
            collection.insert_one(result)

        try:
            url = body.find('a', attrs={'class': 'HH-Pager-Controls-Next'}).attrs['href']
        except AttributeError:
            url = None

        if url:
            self.hh_parse(url=f'{self.hh_base}{url}')


if __name__ == '__main__':
    jobs = JobsParser(verbose=True)
    keyword = 'продавец'
    jobs.superjob_parse(keyword=keyword)
    jobs.hh_parse(keyword=keyword)
