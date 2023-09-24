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

import mastodon

from xpost.social_network import SocialNetwork

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
        return f'Mastodon Account: { self.__user }'

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
