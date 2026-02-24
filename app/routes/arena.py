from flask import Blueprint, render_template, request
from ..services.arena_service import ArenaSearch
import time
import os

arena_bp = Blueprint('arena', __name__)
client = ArenaSearch()

@arena_bp.route('/arena')
def index_arena():
    return render_template('arena.html')

@arena_bp.route('/arena_search', methods=['POST'])
def arena_search():
    global client
    # Re-initialize client if needed or handle singleton properly
    if not hasattr(client, 'client'):
        client = ArenaSearch()
        
    ip = request.access_route[0]
    vid = request.form.get("id")
    with open(os.path.join('config', 'search.txt'), 'a') as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'    '+ip+'    '+str(vid)+'\n')
    msg = client.user_search(vid)
    return msg
