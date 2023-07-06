from flask import Flask, render_template, request, send_from_directory

import os
import json

import config

app = Flask(__name__)

assigned_keys = {}

keys = os.listdir('keys')

if os.path.isfile('assigned_keys.json'):
    with open('assigned_keys.json') as inf:
        assigned_keys = json.load(inf)

def get_key_for_user(username):
    if not username in assigned_keys:
        key = None
        for k in keys:
            if not k in assigned_keys.values():
                key = k
                break
        if not key:
            raise Exception("No more free key")
        assigned_keys[username] = key
        with open('assigned_keys.json', 'w') as outf:
            json.dump(assigned_keys, outf)
    
    return assigned_keys[username]

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/ssh")
def ssh():
    return render_template("ssh.html")

@app.post("/ssh")
def ssh_post():
    token = request.form['token']
    key = request.form['ssh_pub_key']
    if token != config.token:
        return 'Wrong token'
    if not key:
        return 'Where key?'
    if not key.startswith('ssh-'):
        return 'Invalid pubkey'
    try:
        with open('/home/ubuntu/.ssh/authorized_keys', 'a') as sshfile:
            sshfile.write(key + "\n")
        print("Wrote key", key)
        return 'OK'
    except Exception as err:
        return str(err), 500

@app.get("/wireguard")
def wg():
    return render_template("wireguard.html")

@app.post('/wireguard')
def wg_post():
    token = request.form['token']
    username = request.form['username']
    if token != config.token:
        return 'Wrong token'
    try:
        key = get_key_for_user(username)
        print(f'gave key {key} to user {username}')
        return render_template("wireguard.html", key=key, token=token, username=username)
    except Exception as err:
        return str(err), 500
    
@app.post('/wireguard/download')
def wg_download():
    token = request.form['token']
    username = request.form['username']
    if token != config.token:
        return 'Wrong token'
    try:
        key = get_key_for_user(username)
        print(f'sent download key {key} to user {username}')
        return send_from_directory('keys', key)
    except Exception as err:
        return str(err), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=1337)