from telethon.tl.custom import Button
from tg_settings import settings


# *****************************************************************************
def create_admin_user_edit_buttons(user_id):
    btns = []
    btns.append(
        [
            Button.inline("Разблокировать", data=f"/uedit_blocked_0_{user_id}"),
            Button.inline("Заблокировать", data=f"/uedit_blocked_1_{user_id}"),
        ]
    )
    btns.append(
        [
            Button.inline("Админ", data=f"/uedit_admin_1_{user_id}"),
            Button.inline("Не админ", data=f"/uedit_admin_0_{user_id}"),
        ]
    )
    btns.append(
        [
            Button.inline("Удалить из базы", data=f"/uedit_delete_1_{user_id}"),
        ]
    )
    return btns


# *****************************************************************************
def create_admin_start_message():
    msg = "**Команды администратора:**"

    if hasattr(settings, "downloaders"):
        if isinstance(settings.downloaders, list):
            for downloader in settings.downloaders:
                if hasattr(downloader, "admin_commands"):
                    msg += f"\n__Для сайта **{downloader.name}**:__"
                    ind = 0
                    for admin_command in downloader.admin_commands:
                        ind += 1
                        msg += f"\n{ind}. {admin_command.description}"

    msg += f"\n\n__Для генерации ключа для **Audiobooks Orange**:__\n/commands_orange АдресЭлектроннойПочты"

    btns = []
    btns.append([Button.inline("Список пользователей", data="/user_list")])
    btns.append([Button.inline("Последние загрузки", data="/downloads_list")])
    btns.append([Button.inline("Последние команды", data="/commands_list")])
    return msg, btns


# *****************************************************************************
def create_admin_reg_design_buttons(user_id):
    btns = []
    btns.append(
        [Button.inline("Зарегистрировать пользователя", data=f"/reg_accept {user_id}")]
    )
    btns.append([Button.inline("Отклонить запрос", data=f"/reg_decline {user_id}")])
    btns.append(
        [Button.inline("Заблокировать пользователя", data=f"/block_user {user_id}")]
    )
    return btns


# *****************************************************************************
def create_unreg_buttons(user_id):
    btns = [
        Button.inline(
            "Отправить запрос на регистрацию", data=f"/registration_query {user_id}"
        )
    ]
    return btns


# *****************************************************************************
def hello_banner(user_info):
    msg = (
        f"Привет, {user_info}!\n"
        "Вы зарегистрированы и можете пользоваться этим ботом.\n"
        "Он умеет скачивать книги. Просто отправьте "
        "ссылку на страницу с книгой в этот чат.\n"
        f"\n{settings.banner_addition}\n\n"
        "**Скачивать можно:**\n"
    )
    ind = 0
    if hasattr(settings, "downloaders"):
        if isinstance(settings.downloaders, list):
            for downloader in settings.downloaders:
                ind += 1
                msg += f"{ind}. С сайта {downloader.url} \n"
                if hasattr(downloader, "banner_addition"):
                    msg += f"**ВАЖНО!**\n__{downloader.banner_addition}__\n"
    if ind == 0:
        msg += "Ниоткуда нельзя скачивать!!!"
    return msg


# *****************************************************************************
def hello_banner_unreg(user_info):
    return (
        f"Привет, {user_info}, вы не зарегистрированны.\n"
        "Попросить администратора добавить вас в список пользователей?"
    )


# *****************************************************************************
def you_blocked_banner():
    return "К сожалению, вы заблокированы!"


# *****************************************************************************
def user_about_banner(db_user):
    return (
        f"/edit_user_{db_user.id}\n"
        f"    name: {db_user.name}\n"
        f"    admin:{db_user.admin}\n"
        f"    blocked:{db_user.blocked}\n"
    )


# *****************************************************************************
def downloads_banner(db_record):
    return (
        f"{db_record.Books.url}\n"
        f"    user:  {db_record.Books.user} ({db_record.Users.name})\n"
        f"    date: {db_record.Books.date.strftime("%d.%m.%Y %H:%M:%S")}\n"
    )


# *****************************************************************************
def commands_banner(db_record):
    return (
        f"{db_record.CommandsHistory.command}\n"
        f"    user:  {db_record.CommandsHistory.user} ({db_record.Users.name})\n"
        f"    date: {db_record.CommandsHistory.date.strftime("%d.%m.%Y %H:%M:%S")}\n"
    )
