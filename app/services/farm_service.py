from .pcrclient import PCRClient
from json import load, dump
import time
import os

ACCOUNT_PATH = os.path.join('config', 'account.json')

def get_account_data():
    if os.path.exists(ACCOUNT_PATH):
        with open(ACCOUNT_PATH, encoding='utf-8') as fp:
            return load(fp)
    return {}

def save_total(total):
    with open(ACCOUNT_PATH, 'w', encoding='utf-8') as fp:
        dump(total, fp, indent=4, ensure_ascii=False)

def remove_other(clan_id, all_user=False):
    total = get_account_data()
    user_list = []
    if not all_user:
        user_list = total.get("users", [])
    farm_account = total.get("account", [])
    for clan in total.get("clan", []):
        if clan["clan_id"] == clan_id:
            client = PCRClient(clan["owner"])
            client.login(clan["uid"], total["access_key"])
            clan_info = client.callapi('clan/others_info', {'clan_id': clan_id})
            if 'clan' not in clan_info:
                client.login(clan["uid"], total["access_key"])
                clan_info = client.callapi('clan/others_info', {'clan_id': clan_id})
            clean_list = []
            for mem in clan_info['clan']['members']:
                if mem['viewer_id'] not in farm_account and mem['viewer_id'] not in user_list:
                    clean_list.append(mem['viewer_id'])
            clean_count = 0
            for clean_id in clean_list:
                clean_info = client.callapi('clan/remove', {'clan_id': clan_id, 'remove_viewer_id': clean_id})
                if "server_error" not in clean_info:
                    clean_count += 1
            return '工会'+str(clan['clan_id'])+'已清理'+str(clean_count)+'个位置'
    return '未找到工会'

def remove_user(clan_id, remove_id):
    total = get_account_data()
    if isinstance(remove_id, str):
        remove_id = int(remove_id)
    user_list = []
    for user_info in total.get("users", {}).values():
        user_list.append(user_info["vid"])
    for clan in total.get("clan", []):
        if clan["clan_id"] == clan_id:
            client = PCRClient(clan["owner"])
            client.login(clan["uid"], total["access_key"])
            clan_info = client.callapi('clan/others_info', {'clan_id': clan_id})
            if 'clan' not in clan_info:
                client.login(clan["uid"], total["access_key"])
                clan_info = client.callapi('clan/others_info', {'clan_id': clan_id})
            clean_id = 0
            for mem in clan_info['clan']['members']:
                if mem['viewer_id'] == remove_id:
                    clean_id = remove_id
            if not clean_id:
                return str(remove_id)+'不在工会'
            clean_info = client.callapi('clan/remove', {'clan_id': clan_id, 'remove_viewer_id': clean_id})
            if "server_error" not in clean_info:
                return str(remove_id)+'已移出工会'
    return '未找到工会'

def user_clear(clanid, passwd, clear_type):
    total = get_account_data()
    if passwd != total.get("passwd"):
        return "密码错误"

    clan_list = []

    for clan in total.get("clan", []):
        clan_list.append(clan["clan_id"])
    
    remove_list = []
    if not clanid.isdigit():
        return "id非数字"
    elif not int(clanid):
        remove_list = clan_list
    elif int(clanid) in clan_list:
        remove_list.append(int(clanid))
    else:
        return "工会id不在可处理列表内"
    
    msg = ""

    if clear_type == 'clean':
        for join_clan in remove_list:
            msg += remove_other(join_clan)
    elif clear_type == 'remove':
        for join_clan in remove_list:
            msg += remove_other(join_clan, True)
    return msg
