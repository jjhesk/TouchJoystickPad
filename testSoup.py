# !/usr/bin/env python
# coding: utf-8
from lib.twitter.decode import DecodeHTML

if __name__ == '__main__':
    codec = DecodeHTML().fromCache()
    redirection = codec.get_twitter_callback_x()
    if codec.found("Redirecting you back to the application. This may take a few moments."):
        print("it is found!!")
        print(redirection)
    else:
        print("not found")
