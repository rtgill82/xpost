#!/usr/bin/python

import argparse
import sys

import mastodon
import tweepy

MASTODON_USER = 'USERNAME'
MASTODON_PASSWORD = 'PASSWORD'
MASTODON_TOKENS = {
        'api_base_url': 'https://mastodon.social',
        'access_token': 'SECRET',
        'client_id': 'SECRET',
        'client_secret': 'SECRET'
}

TWITTER_TOKENS = {
        'bearer_token': 'SECRET',
        'consumer_key': 'SECRET',
        'consumer_secret': 'SECRET',
        'access_token': 'SECRET',
        'access_token_secret': 'SECRET'
}

class Post:
    def __init__(self, text):
        if len(text) > 280:
            raise RuntimeError('message length is limited to 280 characters')

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
    def __init__(self):
        self.__posts = []

    def add_image(self, image):
        self.__posts[0].add_image(image)

    def post(self, post):
        self.__posts.append(post)

    def posts(self):
        return self.__posts


class Mastodon(SocialNetwork):
    SCOPES = ['write:media', 'write:statuses']

    def __init__(self, user, password, tokens):
        super().__init__()
        self.client = mastodon.Mastodon(**tokens)
        self.client.log_in(user, password, scopes = Mastodon.SCOPES)

    def publish(self):
        reply_id = None
        for post in self.posts():
            response = self.client.status_post(
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
                media = self.client.media_post(image)
                media_ids.append(media.id)

        return media_ids


class Twitter(SocialNetwork):
    def __init__(self, tokens):
        super().__init__()
        self.tokens = tokens
        self.client = tweepy.Client(**tokens)

    def publish(self):
        reply_id = None
        for post in self.posts():
            response = self.client.create_tweet(
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
                    self.tokens['consumer_key'],
                    self.tokens['consumer_secret']
                    )
            auth.set_access_token(
                    self.tokens['access_token'],
                    self.tokens['access_token_secret']
                    )
            api = tweepy.API(auth)

            media_ids = []
            for image in images:
                media = api.media_upload(image)
                media_ids.append(media.media_id)

        return media_ids

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

mastodon = Mastodon(MASTODON_USER, MASTODON_PASSWORD, MASTODON_TOKENS)
twitter = Twitter(TWITTER_TOKENS)

for post in read_messages():
    mastodon.post(post)
    twitter.post(post)

if args.image:
    twitter.add_image(args.image)
    mastodon.add_image(args.image)

mastodon.publish()
twitter.publish()
