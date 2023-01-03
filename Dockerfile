from ubuntu:22.04

maintainer dockerfile@me.recolic.net

run apt update
run DEBIAN_FRONTEND=noninteractive apt install -y python3 python3-pip
run yes | pip3 install python-telegram

run mkdir /app
copy . /app

workdir /app
cmd ["./watchdog.py"]

