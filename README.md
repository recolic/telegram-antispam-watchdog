# Telegram AntiSpam Watchdog

阻止Telegram的私聊骚扰.

[For English README, click Here](README_en.md)

## 此程序会做什么

此软件是一个24小时运行在你的VPS, 服务器, 或其他设备的Python脚本.

它会作为一个Telegram客户端登入你的帐号. 一旦收到私聊信息, 它会抢先阻止消息通知并删除消息, 然后回复一个验证问题.

在对方正确回答问题之前, 它的所有消息都将被静音并删除. 如果对方正确回答了验证问题, 那么此对话中的所有消息将被放行.

需要注意的是, 此脚本会放行所有群组(具有负数id)以及Telegram官方通知(777000)的消息. 你主动发送任何消息也会放行当前私聊会话.

## 如何安装和运行

首先你需要一个运行Linux或MacOS作业系统的24小时开机的设备(例如VPS或云服务器). 你需要安装**Python3和python-telegram**. 以Ubuntu为例, 你可以使用以下命令进行安装:

```
sudo apt install python3 python3-pip
sudo pip3 install python-telegram
```

然后你需要将此仓库下的`watchdog.py`拷贝到你的设备上, 并修改此文件的顶部的几行内容. 如果你不知道如何获取`api_id`和`api_hash`, 烦请阅读[Telegram官方文档](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id).

```
YOUR_QUESTION = '在这里写上你想问的验证问题'
YOUR_ANSWER = '在这里写上正确的答案'
tg = Telegram(
    api_id='在这里写上你的api_id',
    api_hash='在这里写上那一串长长的api_hash',
    phone='在这里写上你的Telegram帐号的手机号码',
    database_encryption_key='any_password',
)
whitelist_filename = 'whitelisted_chats.log'
```

然后您只需要24小时运行刚刚放入伺服器的`watchdog.py`, 就可以了. 注意, 第一次登陆时程序会提示您输入登陆验证码. 

在此之后你可以配置此文件开机自动启动, 或后台运行, 用任何你认为方便的做法.

## Docker

TODO

## 常见问题

暂时没有问题

