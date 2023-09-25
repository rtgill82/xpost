#!/usr/bin/python
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

import argparse
import os
import sys
import tomllib

from xpost import Mastodon, Post, Twitter


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


def read_line():
    try:
        return sys.stdin.readline()
    except KeyboardInterrupt:
        sys.exit(0)


def read_messages():
    message = ''
    line = read_line()

    while line:
         if line == '---\n':
             yield Post(message.rstrip())
             message = ''
             line = read_line()
             continue
         message += line
         line = read_line()
    yield Post(message.rstrip())


def main():
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


if __name__ == "__main__":
    main()
