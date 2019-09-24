# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy.http import HtmlResponse
from urllib.parse import urlencode, urljoin
from copy import deepcopy
from jobparser.items import InstagramLikerItem, InstagramCommentatorItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    variables_base = {'fetch_mutual': 'false', "include_reel": 'true', "first": 100}
    get_posts_base = {'first': 12}
    shortcodes = {}
    likers = {}
    commetators = {}

    def __init__(self, user_links, login, pswrd, *args, **kwargs):
        self.user_links = user_links
        self.login = login
        self.pswrd = pswrd
        self.get_posts_hash = '58b6785bea111c67129decbe6a448951'
        self.get_likers_hash = 'd5d763b1e2acf209d62d22d184488e57'
        self.get_commentators_hash = '97b41c52301f77ce508f55e66d17620e'
        super().__init__(*args, **kwargs)

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            'https://www.instagram.com/accounts/login/ajax/',
            method='POST',
            callback=self.parse_users,
            formdata={'username': self.login, 'password': self.pswrd},
            headers={'X-CSRFToken': csrf_token}
        )

    def parse_users(self, response: HtmlResponse):
        j_body = json.loads(response.body)
        if j_body.get('authenticated'):
            for user in self.user_links:
                if not self.likers.get(user):
                    self.likers[user] = {}
                    self.commetators[user] = {}
                yield response.follow(urljoin(self.start_urls[0], user),
                                      callback=self.parse_user,
                                      cb_kwargs={'user': user})

    def parse_user(self, response: HtmlResponse, user):
        user_id = self.fetch_user_id(response.text, user)
        end_cursor = self.fetch_end_cursor(response.text)
        user_vars = deepcopy(self.get_posts_base)
        user_vars.update({'id': user_id})
        user_vars.update({'end_cursor': end_cursor})
        yield response.follow(self.make_graphql_url(user_vars, self.get_posts_hash),
                              callback=self.get_user_posts,
                              cb_kwargs={'user': user})

    def get_user_posts(self, response: HtmlResponse, user):
        j_body = json.loads(response.text)
        posts = j_body.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')

        for post in posts:
            owner = post.get('node').get('owner').get('username')
            if owner == user:
                if not self.shortcodes.get(user):
                    self.shortcodes[user] = [post.get('node').get('shortcode')]
                else:
                    self.shortcodes[user].append(post.get('node').get('shortcode'))
                if len(self.shortcodes[user]) == 10:
                    break

        for shortcode in self.shortcodes[user]:
            user_vars = deepcopy(self.variables_base)
            user_vars.update({'shortcode': shortcode})

            yield response.follow(self.make_graphql_url(user_vars, self.get_likers_hash),
                                  callback=self.get_likers,
                                  cb_kwargs={'user': user, 'user_vars': user_vars})

            yield response.follow(self.make_graphql_url(user_vars, self.get_commentators_hash),
                                  callback=self.get_commentators,
                                  cb_kwargs={'user': user, 'user_vars': user_vars})

    def get_commentators(self, response: HtmlResponse, user, user_vars):
        j_body = json.loads(response.text)
        data = j_body.get('data').get('shortcode_media').get('edge_media_to_parent_comment')
        edges = data.get('edges')
        count = data.get('count')
        has_next_page = data.get('page_info').get('has_next_page')
        end_cursor = data.get('page_info').get('end_cursor')
        shortcode = user_vars['shortcode']

        if not self.commetators.get(user).get(shortcode):
            self.commetators[user][shortcode] = {
                'commetators': edges,
                'count': count
            }
        else:
            self.commetators[user][shortcode]['commetators'].extend(edges)

        if has_next_page:
            user_vars.update({'after': end_cursor})
            next_page = self.make_graphql_url(user_vars, self.get_commentators_hash)

            yield response.follow(next_page, callback=self.get_commentators,
                                  cb_kwargs={'user': user, 'user_vars': user_vars})

        if not has_next_page:
            for commetator in self.commetators[user][shortcode]['commetators']:
                yield InstagramCommentatorItem(post_owner=user,
                                               post_shortcode=shortcode,
                                               post_url=f'https://www.instagram.com/p/{shortcode}/',
                                               commentator_id=commetator.get('node').get('owner').get('id'),
                                               commentator_username=commetator.get('node').get('owner').get('username'),
                                               commentator_profile_pic_url=commetator.get('node').get('owner').get(
                                                   'profile_pic_url'),
                                               commentator_text=commetator.get('node').get('text'))

    def get_likers(self, response: HtmlResponse, user, user_vars):
        j_body = json.loads(response.text)

        data = j_body.get('data').get('shortcode_media').get('edge_liked_by')
        edges = data.get('edges')
        count = data.get('count')
        has_next_page = data.get('page_info').get('has_next_page')
        end_cursor = data.get('page_info').get('end_cursor')
        shortcode = user_vars['shortcode']

        if not self.likers.get(user).get(shortcode):
            self.likers[user][shortcode] = {
                'likers': edges,
                'count': count
            }
        else:
            self.likers[user][shortcode]['likers'].extend(edges)

        if has_next_page:
            user_vars.update({'after': end_cursor})
            next_page = self.make_graphql_url(user_vars, self.get_likers_hash)

            yield response.follow(next_page, callback=self.get_likers,
                                  cb_kwargs={'user': user, 'user_vars': user_vars})

        if not has_next_page:
            for liker in self.likers[user][shortcode]['likers']:
                yield InstagramLikerItem(post_owner=user,
                                         post_shortcode=shortcode,
                                         post_url=f'https://www.instagram.com/p/{shortcode}/',
                                         liker_id=liker.get('node').get('id'),
                                         liker_username=liker.get('node').get('username'),
                                         liker_full_name=liker.get('node').get('full_name'),
                                         liker_profile_pic_url=liker.get('node').get('profile_pic_url'))

    def fetch_csrf_token(self, text):
        """Используя регулярные выражения парсит переданную строку на наличие
        `csrf_token` и возвращет его."""
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        """Используя регулярные выражения парсит переданную строку на наличие
        `id` нужного пользователя и возвращет его."""
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def make_graphql_url(self, user_vars, hash):
        """Возвращает `url` для `graphql` запроса"""
        result = '{url}query_hash={hash}&variables={variables}'.format(
            url=self.graphql_url, hash=hash,
            variables=json.dumps(user_vars)
        )
        return result

    def fetch_end_cursor(self, text):
        """Используя регулярные выражения парсит переданную строку на наличие
        `end_cursor` и возвращет его."""
        matched = re.search('\"end_cursor\":\"(.*?)\"', text).group()
        return matched.split(':').pop().replace(r'"', '')
