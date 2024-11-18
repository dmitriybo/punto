```
sudo visudo
```
в конец файлов добавить
```
user ALL=(ALL) NOPASSWD: ALL
```
```
sudo nano /etc/systemd/system/keyboard_layout_switcher.service
```
```
[Unit]
Description=Keyboard Layout Switcher
After=display-manager.service

[Service]
ExecStartPre=/bin/sleep 8
ExecStart=/usr/bin/python3 /home/user/keyboard_layout_switcher.py
Environment="DISPLAY=:0"
Environment="DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus"
Restart=always
User=user

[Install]
WantedBy=multi-user.target
```
