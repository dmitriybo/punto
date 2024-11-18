#!/bin/bash

# Получаем текущую раскладку
current_layout=$(sudo -E -u user gdbus introspect --session --dest org.gnome.Shell --object-path /me/madhead/Shyriiwook --only-properties | grep 'currentLayout' | awk -F"'" '{print $2}')

# Проверяем, что раскладка получена
if [ -z "$current_layout" ]; then
    echo "Не удалось получить текущую раскладку."
    exit 1
fi

echo "Текущая раскладка: $current_layout"

# Определяем противоположную раскладку
if [ "$current_layout" == "ru" ]; then
    new_layout="us"
elif [ "$current_layout" == "us" ]; then
    new_layout="ru"
else
    echo "Неизвестная текущая раскладка: $current_layout"
    exit 1
fi

echo "Переключаем на раскладку: $new_layout"

# Переключаем раскладку
sudo -E -u user gdbus call --session --dest org.gnome.Shell --object-path /me/madhead/Shyriiwook --method me.madhead.Shyriiwook.activate "$new_layout"

# Проверяем, что раскладка изменилась
new_current_layout=$(sudo -E -u user gdbus introspect --session --dest org.gnome.Shell --object-path /me/madhead/Shyriiwook --only-properties | grep 'currentLayout' | awk -F"'" '{print $2}')
echo "Теперь текущая раскладка: $new_current_layout"
