#!/usr/bin/python3 -u
from telegram.client import Telegram
import threading, time, os

##################### Configuration Begin ######################
YOUR_QUESTION = '12 + 17 = ?'
YOUR_ANSWER = '29'
tg = Telegram(
    api_id='11111111', # Get api_id and api_hash at my.telegram.org
    api_hash='c70111111111111111111111111111b5',
    phone='+13331112222',
    database_encryption_key='any_password',
    files_directory='tdlib_files/',
)
aggresive_mode = True # Delete the chat on your side after sending verification message. The reason is `mark_msg_read()` cannot always eliminate the notification successfully.
##################### Configuration End ########################

whitelist_filename = 'whitelisted_chats.log'
whitelisted_chat_ids = []

magic_text = '[tqYH5C]'
msg_verify = 'This account is protected by Telegram Antispam WatchDog.\nPlease answer the question to continue:\n请正确回答以下问题:\n\n' + YOUR_QUESTION
msg_whitelisted = '[Telegram Antispam Watchdog] Whitelisted this chat.'

# We need to mark_message_read() for 30 times, with one second interval. That's the only method to eliminate GMS notification.
# Format: [(chat_id, msg_id, count), ...]
# count will decrease from 30 to 0 by a timer in another thread.
remove_gms_notify_queue = []
remove_gms_notify_queue_lock = threading.Lock()

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
    # This function must be called multiple times. For example, call it once a second, for 8 times.
    # You must call mark_msg_read_finish() after the last mark_msg_read(). You must wait as long as possible before calling mark_msg_read_finish(), to make the mark_msg_read reliable.
    # This problem only appears in GMS notification.
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

def mark_msg_read_finish(chat_id):
    fn_data = {
        '@type': 'closeChat',
        'chat_id': chat_id,
    }
    tg._tdjson.send(fn_data)

def timer_handler():
    # In every second, check if there is any message to be marked as read.
    global remove_gms_notify_queue
    with remove_gms_notify_queue_lock:
        result_list = []
        for entry in remove_gms_notify_queue:
            chat_id, msg_id, count = entry
            mark_msg_read(chat_id, msg_id)
            if count-1 > 0:
                result_list.append((chat_id, msg_id, count-1))
            else:
                mark_msg_read_finish(chat_id)
        remove_gms_notify_queue = result_list

def new_message_handler(update):
    chat_id = update['message']['chat_id']
    msg_id = update['message']['id']
    message_content = update['message']['content']
    is_outgoing = update['message']['is_outgoing']
    message_text = message_content.get('text', {}).get('text', '')

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
        # Send any outgoing message to add unknown chat to whitelist. (Except verification message)
        if magic_text not in message_text:
            whitelisted_chat_ids.append(chat_id)
            write_whitelist_to_disk(whitelist_filename)
            tg.send_message(chat_id=chat_id, text=msg_whitelisted)
        return

    print("DEBUG: Received a new private chat message which needs verification, chat_id=", chat_id)

    # Mark as read to suppress the notification.
    mark_msg_read(chat_id, msg_id)

    if message_content['@type'] == 'messageText' and message_text.lower() == YOUR_ANSWER.lower():
        # Answer is correct: add to whitelist and send hello
        print("DEBUG: good answer")
        whitelisted_chat_ids.append(chat_id)
        write_whitelist_to_disk(whitelist_filename)
        tg.send_message(chat_id=chat_id, text='You have passed the verification. Thanks.')
    else:
        # Answer is not correct: send verification message and delete his message.
        print("DEBUG: bad answer")
        tg.send_message(chat_id=chat_id, text=magic_text + msg_verify)
        tg.delete_messages(chat_id, [msg_id])
        with remove_gms_notify_queue_lock:
            remove_gms_notify_queue.append((chat_id, msg_id, 16))

def timer_thread_func():
    while True:
        timer_handler()
        time.sleep(1)

if __name__ == "__main__":
    read_whitelist_from_disk(whitelist_filename)
    tg.login()
    
    # if this is the first run, library needs to preload all chats
    # otherwise the message will not be sent
    result = tg.get_chats()
    result.wait()
    print("Started Telegram Antispam Watchdog. API test by listing your chats: ", result.update)

    threading.Thread(target=timer_thread_func).start()

    tg.add_message_handler(new_message_handler)
    tg.idle()  # blocking waiting for CTRL+C
    tg.stop()  # you must call `stop` at the end of the script
    print("Exited")
    os._exit(0)

