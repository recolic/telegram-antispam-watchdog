# Telegram AntiSpam Watchdog

Automatically block telegram private message spammer for you!

[Chinese Version](README.md)

## What does this program do

This is a python script which runs on your VPS / Server 24 hours.

It logs into your Telegram account just like a normal telegram client. Once receiving a private message, it will block the notification and delete it, and then send a verification question as reply.

All private messages from the peer will be muted and deleted until he answers the verification question correctly.

Note that this program will whitelist all messages from Group/Channel (with negative chat id) and Telegram official notification (777000). The current chat will be whitelisted if you send any outgoing messages.

## How to install and run

You need a Linux/MacOS device, and then install **python3 and python-telegram** on it. For example, if you are using ubuntu, you should run this:

```
sudo apt install python3 python3-pip
sudo pip3 install python-telegram
```

And then copy the `watchdog.py` onto your device. Modify the following lines at the top of the file. Refer to [Telegram Official Document](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id) about how to get `api_id` and `api_hash`.

```
YOUR_QUESTION = 'Your verification question here'
YOUR_ANSWER = 'Your expected answer here'
TELEGRAM_API_ID = 'Change This!'
TELEGRAM_API_HASH = 'Change This!'
TELEGRAM_PHONE = 'Phone number of your telegram account'
```

Now you just need to run the modified `watchdog.py` 24 hours a day. Note that you need to input the SMS code on the first login.

## Docker

TODO

## FAQ

No question yet.

