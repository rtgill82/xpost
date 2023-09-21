#!/usr/bin/python

import argparse
import os
import sys
import tomllib

import mastodon
import tweepy

class Post:
    def __init__(self, text):
        self.__text = text
        self.__images = None

    def add_image(self, image):
        if self.__images is None:
            self.__images = []

        if len(self.__images) > 3:
            raise IndexError('the number of images attached to a post is limited to 4')

        if image not in self.__images:
            self.__images.append(image)

    def images(self):
        return self.__images

    def text(self):
        return self.__text

class SocialNetwork:
    CHAR_LIMIT = 0
    IMAGE_LIMIT = 0

    def __init__(self):
        self.__posts = []

    def add_image(self, image):
        if len(self.__posts[0].images()) > self.IMAGE_LIMIT:
            raise RuntimeError(f'image attachments are limited to { self.IMAGE_LIMIT } images')
        self.__posts[0].add_image(image)

    def limit(self):
        return self.CHAR_LIMIT

    def post(self, post):
        if len(post.text()) > self.CHAR_LIMIT:
            raise RuntimeError(f'message length is limited to { self.CHAR_LIMIT } characters')
        self.__posts.append(post)

    def posts(self):
        return self.__posts


class Mastodon(SocialNetwork):
    CHAR_LIMIT = 500
    IMAGE_LIMIT = 4

    SCOPES = ['write:media', 'write:statuses']

    def __init__(self, config):
        super().__init__()
        self.__user = config.user()
        self.__client = mastodon.Mastodon(**config.tokens())
        self.__client.log_in(self.__user, config.password(),
                             scopes = Mastodon.SCOPES)

    def publish(self):
        reply_id = None
        for post in self.posts():
            response = self.__client.status_post(
                    post.text(),
                    in_reply_to_id = reply_id,
                    media_ids = self.__upload(post)
                    )
            reply_id = response.id

    def __upload(self, post):
        media_ids = None
        images = post.images()
        if images:
            media_ids = []

            for image in images:
                media = self.__client.media_post(image)
                media_ids.append(media.id)

        return media_ids

    def __str__(self):
        return f'{ self.__user }@Mastodon'

    class Config:
        def __init__(self, **kwargs):
            self.__user = kwargs['user']
            self.__password = kwargs['password']
            self.__tokens = {
                'api_base_url': kwargs['api_base_url'],
                'client_id': kwargs['client_key'],
                'client_secret': kwargs['client_secret'],
                'access_token': kwargs['access_token'],
            }

        def user(self):
            return self.__user

        def password(self):
            return self.__password

        def tokens(self):
            return self.__tokens


class Twitter(SocialNetwork):
    CHAR_LIMIT = 500
    IMAGE_LIMIT = 4

    def __init__(self, config):
        super().__init__()
        self.__user = config.user()
        self.__tokens = config.tokens()
        self.__client = tweepy.Client(**tokens)

    def publish(self):
        reply_id = None
        for post in self.posts():
            response = self.__client.create_tweet(
                    text = post.text(),
                    in_reply_to_tweet_id = reply_id,
                    media_ids = self.__upload(post)
                    )
            reply_id = response.data['id']

    def __upload(self, post):
        media_ids = None
        images = post.images()
        if images:
            auth = tweepy.OAuthHandler(
                    self.__tokens['consumer_key'],
                    self.__tokens['consumer_secret']
                    )
            auth.set_access_token(
                    self.__tokens['access_token'],
                    self.__tokens['access_token_secret']
                    )
            api = tweepy.API(auth)

            media_ids = []
            for image in images:
                media = api.media_upload(image)
                media_ids.append(media.media_id)

        return media_ids

    def __str__(self):
        return f'{ self.__user }@Twitter'

    class Config:
        def __init__(self, **kwargs):
            self.__tokens = {
                'user': kwargs['user'],
                'consumer_key': kwargs['api_key'],
                'consumer_secret': kwargs['api_secret'],
                'bearer_token': kwargs['bearer_token'],
                'access_token': kwargs['access_token'],
                'access_token_secret': kwargs['access_token_secret']
            }

        def user(self):
            return self.__tokens['user']

        def tokens(self):
            return self.__tokens

def read_config():
    accounts = []
    home = os.getenv('HOME')
    if home == None:
        print('Unable to locate HOME directory.')
        sys.exit(1)
    path = f"{ home }/.xpostrc"
    with open(f'{ home }/.xpostrc', 'rb') as f:
        data = tomllib.load(f)
        if 'mastodon' in data:
            for account in data['mastodon']:
                config = Mastodon.Config(**account)
                accounts.append(Mastodon(config))

        if 'twitter' in data:
            for account in data['twitter']:
                config = Twitter.Config(**account)
                accounts.append(Twitter(config))

    return accounts

def read_messages():
    message = ''
    line = sys.stdin.readline()
    while line:
         if line == '---\n':
             yield Post(message.rstrip())
             message = ''
             line = sys.stdin.readline()
             continue
         message += line
         line = sys.stdin.readline()
    yield Post(message.rstrip())

parser = argparse.ArgumentParser(
        prog = 'xpost.py',
        description = 'Mastodon and Twitter cross-poster'
        )

parser.add_argument('-i', '--image', help = 'attach an image to post')
args = parser.parse_args()

accounts = read_config()

for post in read_messages():
    for account in accounts:
        account.post(post)

if args.image:
    for account in accounts:
        account.add_image(args.image)

for account in accounts:
    account.publish()
