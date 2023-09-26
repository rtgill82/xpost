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

from atproto import Client, exceptions, models

from xpost.social_network import SocialNetwork

class Bsky(SocialNetwork):
    CHAR_LIMIT = 300
    IMAGE_LIMIT = 4

    def __init__(self, config):
        super().__init__()
        self.__user = config.user()
        self.__password = config.password()
        self.__client = Client()

    def publish(self):
        response = None
        client = self.__connect()

        for post in self.posts():
            response = client.send_post(
                    text = post.text(),
                    reply_to = _reply_ref(response),
                    embed = _embed_ref(client, post)
                    )

    def __connect(self):
        self.__client.login(self.__user, self.__password)
        return self.__client

    def __str__(self):
        return f'Bsky Account: { self.__user }'

    class Config:
        def __init__(self, **kwargs):
            self.__user = kwargs['user']
            self.__password = kwargs['password']

        def user(self):
            return self.__user

        def password(self):
            return self.__password


def _embed_ref(client, post):
    embed_ref = None

    images = post.images()
    if len(images) > 0:
        image_refs = []
        for image in images:
            with open(image, 'rb') as f:
                upload = _upload_blob(client, f.read())
                image_ref = models.AppBskyEmbedImages.Image(
                        alt = '',
                        image = upload.blob
                        )
                image_refs.append(image_ref)

        embed_ref = models.AppBskyEmbedImages.Main(images = image_refs)

    return embed_ref


def _reply_ref(response):
    reply_ref = None

    if response != None:
        ref = models.create_strong_ref(response)
        reply_ref = models.AppBskyFeedPost.ReplyRef(parent = ref, root = ref)

    return reply_ref


def _upload_blob(client, data):
    exception = None
    upload = None

    for _ in range(3):
        try:
            upload = client.com.atproto.repo.upload_blob(data)
        except exceptions.InvokeTimeoutError as e:
            exception = e
            continue
        else:
            break

    if upload == None and Exception != None:
        raise exception

    return upload
