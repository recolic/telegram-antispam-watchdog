#!/usr/bin/python3 -u
from telegram.client import Telegram

##################### Configuration Begin ######################
YOUR_QUESTION = '12 + 17 = ?'
YOUR_ANSWER = '29'
tg = Telegram(
    api_id='11111111', # Get api_id and api_hash at my.telegram.org
    api_hash='11111111111111111111111111111111111111111',
    phone='+15012212221',
    database_encryption_key='any_password',
    files_directory='tdlib_files/',
)
whitelist_filename = 'whitelisted_chats.log'
##################### Configuration End ########################

whitelisted_chat_ids = []

def read_whitelist_from_disk(fname):
    try:
        with open(fname, 'r') as f:
            for l in f.read().split('\n'):
                if l != '':
                    whitelisted_chat_ids.append(int(l))
    except FileNotFoundError:
        pass

def write_whitelist_to_disk(fname):
    with open(fname, 'w+') as f:
        f.write('\n'.join([str(i) for i in whitelisted_chat_ids]))

def mark_msg_read(chat_id, msg_id):
    fn_data = {
        '@type': 'openChat',
        'chat_id': chat_id,
    }
    tg._tdjson.send(fn_data)

    fn_data = {
        '@type': 'viewMessages',
        'chat_id': chat_id,
        'message_ids': [msg_id],
        'force_read': True,
    }
    tg._tdjson.send(fn_data)

    fn_data = {
        '@type': 'closeChat',
        'chat_id': chat_id,
    }
    tg._tdjson.send(fn_data)

def new_message_handler(update):
    chat_id = update['message']['chat_id']
    msg_id = update['message']['id']
    message_content = update['message']['content']
    is_outgoing = update['message']['is_outgoing']
    message_text = message_content.get('text', {}).get('text', '').lower()

    # This handler will block all message which satisfies ALL of the following condition:
    # 1. Incoming
    # 2. Not from group chat (Personal chat)
    # 3. chat_id is not in whitelist
    # 4. chat_id is not 777000 (Telegram official notification)
    # Maybe we can whitelist sender_id instead of chat_id, but I think it doesn't make a difference.

    if chat_id < 0 or chat_id == 777000:
        return
    if chat_id in whitelisted_chat_ids:
        return
    if is_outgoing:
        # Send any outgoing message to add unknown chat to whitelist.
        if not message_text.startswith('This account is protected by Telegram Antispam WatchDog.'):
            whitelisted_chat_ids.append(chat_id)
            write_whitelist_to_disk(whitelist_filename)
            tg.send_message(chat_id=chat_id, text='[Telegram Antispam Watchdog] Whitelisted this chat.')
        return

    print("DEBUG: Received a new private chat message which needs verification, chat_id=", chat_id)

    # Mark as read to suppress the notification.
    mark_msg_read(chat_id, msg_id)

    if message_content['@type'] == 'messageText' and message_text == YOUR_ANSWER.lower():
        # Answer is correct: add to whitelist and send hello
        print("DEBUG: good answer")
        whitelisted_chat_ids.append(chat_id)
        write_whitelist_to_disk(whitelist_filename)
        tg.send_message(chat_id=chat_id, text='You have passed the verification. Thanks.')
    else:
        # Answer is not correct: send verification message and delete his message.
        print("DEBUG: bad answer")
        tg.send_message(chat_id=chat_id, text='This account is protected by Telegram Antispam WatchDog.\nPlease answer the question to continue:\n请正确回答以下问题:\n\n' + YOUR_QUESTION)
        tg.delete_messages(chat_id, [msg_id])

if __name__ == "__main__":
    read_whitelist_from_disk(whitelist_filename)
    tg.login()
    
    # if this is the first run, library needs to preload all chats
    # otherwise the message will not be sent
    result = tg.get_chats()
    result.wait()
    print("Started Telegram Antispam Watchdog. API test by listing your chats: ", result.update)
    
    tg.add_message_handler(new_message_handler)
    tg.idle()  # blocking waiting for CTRL+C
    tg.stop()  # you must call `stop` at the end of the script

