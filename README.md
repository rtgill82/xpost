
# xpost.py

*Social network cross posting utility*

A simple command line utility that cross-posts between different social
networks. Currently Mastodon, Bluesky, and Twitter (X) are supported. Enter
the text of your post on STDIN. A single image can also be attached to the
post. Requires Python3.

## Usage

```
usage: xpost.py [-h] [-i IMAGE]

Mastodon and Twitter cross-poster

options:
  -h, --help            show this help message and exit
    -i IMAGE, --image IMAGE
                            attach an image to post
```
