#! /bin/bash
DIR=$(pwd $(dirname $0))
echo $DIR
cd $DIR

VENV_NAME=".venv"
SERVICE_NAME="tg-combine"
SERVICE_FILE_NAME=$SERVICE_NAME".service"

echo "**********************************************************************"
echo "* Создание виртуального окружения"
echo
python3 -m venv $VENV_NAME

echo
echo "**********************************************************************"
echo "* Установка зависимостей"
echo

source $VENV_NAME/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "
[Unit]
Description=Телеграм бот ($SERVICE_NAME)
After=network.target

[Service]
Type=simple
User=root
Group=root

Environment=VIRTUAL_ENV=$DIR/$VENV_NAME
Environment=PYTHONPATH=$DIR

WorkingDirectory=$DIR
ExecStart=$DIR/$VENV_NAME/bin/python3 $DIR/tg_combine.py

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target" > $SERVICE_FILE_NAME

echo
echo "**********************************************************************"
echo "* Перед первым запуском необходимо задать настройки"
echo "* 1. Создать файл настроек:"
echo "* cp settings_example.yml settings.yml"
echo "* 2. Отредактировать настройки в любом текстовом редакторе. Например:"
echo "* nano settings.yml"
echo "*"
echo "* Для запуска бота используйте команду:"
echo "* ./$SERVICE_NAME.sh"
echo "*"
echo "*"
echo "*"
echo "* Для запуска бота как службы необходимо выполнить команды:"
echo "*"
echo "* sudo mv $SERVICE_FILE_NAME /etc/systemd/system/$SERVICE_FILE_NAME"
echo "* sudo systemctl enable $SERVICE_FILE_NAME"
echo "* sudo service $SERVICE_NAME start "
echo "*"
echo "* Проверка состояния службы:"
echo "* sudo service $SERVICE_NAME status"
echo "*"
echo "* Остановка службы:"
echo "* sudo service $SERVICE_NAME stop"
echo "*"
echo "*"
echo "*"
echo "* Удаление службы:"
echo "* sudo service $SERVICE_NAME stop"
echo "* sudo systemctl disable $SERVICE_FILE_NAME"
echo "* sudo rm /etc/systemd/system/$SERVICE_FILE_NAME"
echo "*"
echo "*"
echo "**********************************************************************"
