from .pcrclient import PCRClient
from json import load, dump
import time
import os

# Load account.json from root
def get_account_data():
    if os.path.exists('account.json'):
        with open('account.json', encoding='utf-8') as fp:
            return load(fp)
    return {}

class ArenaSearch:
    def __init__(self):
        self.total = get_account_data()
        if not self.total:
            print("Warning: account.json not found or empty.")
            return
        self.account = self.total.get("arena_account", {})
        if self.account:
            self.client = PCRClient(self.account["vid"])
            self.client.login(self.account["uid"], self.total["access_key"])

    def user_search(self, user_id):
        if not self.total:
             return '配置文件缺失'
        
        if len(str(user_id)) != 13:
            return '请输入13位数字'
        req = self.client.callapi('profile/get_profile', {'target_viewer_id': int(user_id)})
        if "server_error" in req:
            self.client.login(self.account["uid"], self.total["access_key"])
            with open('reload.log', 'a') as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'  reload')
            print('重新登录')
            req = self.client.callapi('profile/get_profile', {'target_viewer_id': int(user_id)})
        msg = "未查询到信息"
        if 'user_info' in req and req['user_info']['viewer_id'] == int(user_id):
            user_name = req['user_info']['user_name']
            arena_group = req['user_info']['arena_group']
            grand_arena_group = req['user_info']['grand_arena_group']
            msg = '用户昵称: ' + user_name + '<br/>竞技场场次: ' + str(arena_group) + '<br/>公主竞技场场次: ' + str(grand_arena_group)
        return msg
