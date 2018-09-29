WIP

# minecraftd
Minecraft server daemonizer for systemd compatiblity

## What dis?
This is a replacement for 'screen' when you run a Minecraft (or Spigot) using systemd (or any other init system)

## Why dis?
I find it an ugly hack, to use screen with systemd, and I had weird issues with it.
Since google led me nowhere with this problem, I decided to write my own script for it.

## Usage

### How to install:

???

### How to setup:
First of all, you need a designated user to run your minecraft instance:
```bash
# addgroup ...
# adduser ...
```
After that you should edit the config file:
```

???
```

With systemd you should create this systemd unit:
```ini
[Unit]
Description=Minecraft Server
After=network-online.target

[Service]
Type=simple
User=minecraft
Group=minecraft
WorkingDirectory=/opt/minecraft
Restart=never
ExecStart=...
ExecStop=...
KillMode=process
KillSignal=SIGINT

[Install]
WantedBy=multi-user.target
```
Save it to /etc/systemd/system/minecraft.service
And then enable and start it:
```bash
# systemctl daemon-reload
# systemctl enable minecraft
# systemctl start minecraft
```
And you are done!

### How to use:
When the minecraftd is running, you can access the console with the following command:
```
???
```

You can stop or restart the minecraft server with systemctl from now on:
```bash
# systemctl stop minecraft
# systemctl restart minecraft
```
