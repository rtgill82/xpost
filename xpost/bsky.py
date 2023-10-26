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

from atproto import AtUri, Client, exceptions, models
from xpost.social_network import SocialNetwork

class Bsky(SocialNetwork):
    CHAR_LIMIT = 300
    IMAGE_LIMIT = 4

    def __init__(self, config):
        super().__init__()
        self.__user = config.user()
        self.__password = config.password()
        self.__logged_in = False

    def client(self):
        self._client = self._client or Client()
        if not self.__logged_in:
            self._client.login(self.__user, self.__password)

        return self._client

    def publish(self):
        response = None
        post_ids = []

        client = self.client()
        for post in self.posts():
            try:
                response = self._try(self._send_post, post, response)
            except Exception as e:
                self.delete(*post_ids)
                raise e

            post_ids.append(response)

        return post_ids

    def delete(self, *posts):
        client = self.client()
        for post in posts:
            try:
                rkey = AtUri.from_str(post.uri).rkey
                self._try(client.delete_post, rkey, retries=5)
            except Exception as e:
                print(f'Unable to delete post: { e }.', file=sys.stderr)
                next

    def _send_post(self, post, response = None):
        response = self.client().send_post(
                text = post.text(),
                reply_to = _reply_ref(response),
                embed = self._embed_ref(post)
                )

        return response

    def _embed_ref(self, post):
        embed_ref = None
        images = post.images()

        client = self.client()
        upload_blob = lambda data: client.com.atproto.repo.upload_blob(data)

        if len(images) > 0:
            image_refs = []
            for image in images:
                with open(image, 'rb') as f:
                    upload = self.__try(upload_blob, f.read())
                    image_ref = models.AppBskyEmbedImages.Image(
                            alt = '',
                            image = upload.blob
                            )
                    image_refs.append(image_ref)

            embed_ref = models.AppBskyEmbedImages.Main(images=image_refs)

        return embed_ref

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


def _reply_ref(response):
    reply_ref = None

    if response:
        ref = models.create_strong_ref(response)
        reply_ref = models.AppBskyFeedPost.ReplyRef(parent=ref, root=ref)

    return reply_ref
