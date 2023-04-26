import time

from flask import Flask, request, jsonify, render_template

import farm
import arena

client = arena.ArenaSearch()

app = Flask(__name__)
app.debug = False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/farm')
def index_farm():
    return render_template('farm.html')


@app.route('/remove_user', methods=['POST'])#路由
def test_post():
    qq = request.form.get("qq")
    vid = request.form.get("id")
    clear_type = request.form.get("type")
    msg = farm.user_clear(qq, vid, clear_type)
    return msg


@app.route('/arena')
def index_arena():
    return render_template('arena.html')


@app.route('/arena_search', methods=['POST'])# 路由
def arena_search():
    global client
    ip = request.access_route[0]
    vid = request.form.get("id")
    with open('search.txt', 'a') as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'    '+ip+'    '+vid+'\n')
    msg = client.user_search(vid)
    return msg


if __name__ == '__main__':
    # 这里指定了地址和端口号。
    app.run(host='0.0.0.0', debug=True, port=8000)
