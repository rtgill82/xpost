#
# Copyright (c) 2022,2023 Robert Gill <rtgill82@gmail.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import tweepy

from xpost.social_network import SocialNetwork

class Twitter(SocialNetwork):
    CHAR_LIMIT = 500
    IMAGE_LIMIT = 4

    def __init__(self, config):
        super().__init__()
        self.__user = config.user()
        self.__tokens = config.tokens()
        self.__client = tweepy.Client(**self.__tokens)

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
        return f'Twitter Account: { self.__user }'

    class Config:
        def __init__(self, **kwargs):
            self.__user = kwargs['user']
            self.__tokens = {
                'consumer_key': kwargs['api_key'],
                'consumer_secret': kwargs['api_secret'],
                'bearer_token': kwargs['bearer_token'],
                'access_token': kwargs['access_token'],
                'access_token_secret': kwargs['access_token_secret']
            }

        def user(self):
            return self.__user

        def tokens(self):
            return self.__tokens
