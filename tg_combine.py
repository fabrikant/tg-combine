import logging
import tg_combine_db as db
from telethon import TelegramClient, events
from telethon.tl.custom import Button

import subprocess
from keys import (
    BOT_TOKEN,
    API_ID,
    API_HASH,
    DB_FILENAME,
    DOWNLOAD_COMMAND,
    DOWNLOAD_PATH,
    COOKIES_FILE,
)

COMMAND_START = "/start"
COMMAND_QUERY_REG = "/registration"
COMMAND_ACCEPT_REG = "/accept_registration"
COMMAND_DECLINE_REG = "/decline_registration"
COMMAND_BLOCK_USER = "/block_user"
COMMAND_LIST_USER = "/list_user"

db_session = db.create_database(f"sqlite:///{DB_FILENAME}")
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)


# *****************************************************************************
async def user_info(user_or_id):
    if type(user_or_id) == type(1):
        user = await client.get_entity(user_or_id)
    else:
        user = user_or_id

    info = user.first_name
    if user.last_name != None:
        info += f" {user.last_name}"
    if user.phone != None:
        info += f" ({user.phone})"
    return info


# *****************************************************************************
def create_butons(commands):
    btns = []
    for command in commands:
        btns.append(
            [
                Button.text(
                    command,
                    resize=True,
                    single_use=True,
                    selective=True,
                )
            ]
        )
    return btns


# *****************************************************************************
@client.on(events.NewMessage(pattern=COMMAND_START))
async def start(event):
    sender_id = event.sender_id
    name = await user_info(event.sender)

    if  db.user_is_valid(db_session, sender_id):
        await event.respond(
            f"Привет, {name}, вы не зарегистрированны. Попросить администратора добавить вас в список пользователей?",
            buttons=create_butons(
                [
                    f"{COMMAND_QUERY_REG}",
                ]
            ),
        )
    else:
        if db.user_is_admin(db_session, sender_id):
            await event.respond("Вы администратор")
        else:
            await event.respond(
                f"Привет, {name}, вы зарегистрированный пользователь и у вас есть следующие возможности:"
            )


# *****************************************************************************
@client.on(events.NewMessage(pattern=f"{COMMAND_ACCEPT_REG}(.+)"))
async def accept_registration(event):
    # если команда не от админа, ничего не делаем
    if not db.user_is_admin(db_session, event.sender_id):
        return
    # Создаем пользователя
    new_user_id = int(event.pattern_match.group(1))
    new_user_info = await user_info(new_user_id)
    db.get_or_create(
        db_session,
        db.Users,
        True,
        id=new_user_id,
        name=new_user_info,
        admin=False,
        blocked=False,
    )
    # Нужно сообщить пользователю о регистрации
    await client.send_message(new_user_id, "Заявка на регистрацию одобрена")


# *****************************************************************************
@client.on(events.NewMessage(pattern=f"{COMMAND_BLOCK_USER}(.+)"))
async def block_user(event):
    # если команда не от админа, ничего не делаем
    if not db.user_is_admin(db_session, event.sender_id):
        return
    # Создаем пользователя
    new_user_id = int(event.pattern_match.group(1))
    new_user_info = await user_info(new_user_id)
    db.get_or_create(
        db_session,
        db.Users,
        True,
        id=new_user_id,
        name=new_user_info,
        admin=False,
        blocked=True,
    )
    # Нужно сообщить пользователю о регистрации
    await client.send_message(new_user_id, "Вы заблокированы")


# *****************************************************************************
@client.on(events.NewMessage(pattern=f"{COMMAND_DECLINE_REG}(.+)"))
async def decline_registration(event):
    # если команда не от админа, ничего не делаем
    if not db.user_is_admin(db_session, event.sender_id):
        return
    # Создаем пользователя
    new_user_id = int(event.pattern_match.group(1))

    # Нужно сообщить пользователю об отказе в регистрации
    await client.send_message(new_user_id, "Заявка на регистрацию отклонена")


# *****************************************************************************
@client.on(events.NewMessage(pattern=COMMAND_QUERY_REG))
async def registration(event):
    sender_id = event.sender_id
    sender = event.sender
    sender_info = await user_info(sender)

    # Отправляем запрос администраторам
    db_query = (
        db_session.query(db.Users)
        .filter(db.Users.admin == True)
        .filter(db.Users.blocked == False)
        .all()
    )
    for db_admin in db_query:
        msg = f"Запрос на регистрацию от пользователя: {sender_info}"
        await client.send_message(
            db_admin.id,
            msg,
            buttons=create_butons(
                [
                    f"{COMMAND_ACCEPT_REG} {sender_id}",
                    f"{COMMAND_DECLINE_REG} {sender_id}",
                    f"{COMMAND_BLOCK_USER} {sender_id}",
                ]
            ),
        )
    # Отправляем ответ пользователю
    await event.respond(
        f"Администратору отправлен запрос на регистрацию. Ожидайте решения!"
    )


# *****************************************************************************
@client.on(events.NewMessage(pattern="https://www.litres.ru/audiobook/(.+)"))
async def litres_url(event):
    url = event.text
    user_id = event.sender_id
    db_user = db.get_user(db_session, user_id)
    if db_user == None:
        user_info = await user_info(event.sender)
        await event.respond(f"Уходи, {user_info}, я тебя не знаю!!!")
    else:
        subprocess.Popen(
            f"{DOWNLOAD_COMMAND} --telegram-api {BOT_TOKEN} --telegram-chatid {event.chat_id} \
            --cookies-file {COOKIES_FILE} --output {DOWNLOAD_PATH} --url {url}",
            shell=True,
        )


# *****************************************************************************
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    client.start()
    client.run_until_disconnected()
