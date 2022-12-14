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

class Mastodon:
    SCOPES = ['write:media', 'write:statuses']

    def __init__(self, user, password, tokens):
        self.client = mastodon.Mastodon(**tokens)
        self.client.log_in(user, password, scopes = Mastodon.SCOPES)
        self.media_ids = None

    def upload(self, image):
        if self.media_ids is None:
            self.media_ids = []

        if len(self.media_ids) > 3:
            raise IndexError('the number of images attached to a post is limited to 4')

        media = self.client.media_post(image)
        self.media_ids.append(media.id)
        return self.media_ids

    def post(self, message):
        response = self.client.status_post(
                message,
                media_ids = self.media_ids
                )
        self.media_ids = None
        return response

class Twitter:
    def __init__(self, tokens):
        self.tokens = tokens
        self.client = tweepy.Client(**tokens)
        self.media_ids = None

    def upload(self, image):
        if self.media_ids is None:
            self.media_ids = []

        if len(self.media_ids) > 3:
            raise IndexError('the number of images attached to a post is limited to 4')

        auth = tweepy.OAuthHandler(
                self.tokens['consumer_key'],
                self.tokens['consumer_secret']
                )
        auth.set_access_token(
                self.tokens['access_token'],
                self.tokens['access_token_secret']
                )
        api = tweepy.API(auth)

        media = api.media_upload(image)
        self.media_ids.append(media.media_id)
        return self.media_ids

    def post(self, message):
        response = self.client.create_tweet(
                text = message,
                media_ids = self.media_ids
                )
        self.media_ids = None
        return response

def read_message():
    message = sys.stdin.read()
    if len(message) > 280:
        print('message is too long')
        sys.exit(1)
    return message

parser = argparse.ArgumentParser(
        prog = 'xpost.py',
        description = 'Mastodon and Twitter cross-poster'
        )

parser.add_argument('-i', '--image', help = 'attach an image to post')
args = parser.parse_args()

message = read_message()
mastodon = Mastodon(MASTODON_USER, MASTODON_PASSWORD, MASTODON_TOKENS)
twitter = Twitter(TWITTER_TOKENS)

twitter_media = None
mastodon_media = None
if args.image:
    twitter_media = twitter.upload(args.image)
    mastodon_media = mastodon.upload(args.image)

mastodon.post(message)
twitter.post(message)
