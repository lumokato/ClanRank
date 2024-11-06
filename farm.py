from pcrclient import PCRClient
from json import load, dump
import time

with open('account.json', encoding='utf-8') as fp:
    total = load(fp)


def save_total():
    global total
    with open('account.json', 'w', encoding='utf-8') as fp:
        dump(total, fp, indent=4, ensure_ascii=False)


def remove_other(clan_id, all_user=False):
    user_list = []
    if not all_user:
        for user_info in total["users"].values():
            user_list.append(user_info["vid"])
    farm_account = total["account"]
    for clan in total["clan"]:
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
            return '工会'+clan['name']+'已清理'+str(clean_count)+'个位置'


def remove_user(clan_id, remove_id):
    if isinstance(remove_id, str):
        remove_id = int(remove_id)
    user_list = []
    for user_info in total["users"].values():
        user_list.append(user_info["vid"])
    for clan in total["clan"]:
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


def user_clear(clanid, passwd, clear_type):
    req_time = time.time()
    user_type = 'none'
    if passwd != total["passwd"]:
        return "密码错误"

    clan_list = []
    for clan in total["clan"]:
        clan_list.append[clan["clan_id"]]
    
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

    # if clear_type == 'clean':
    #     for join_clan in remove_list:
    #         msg += remove_other(join_clan)
    # elif clear_type == 'remove':
    #     for join_clan in remove_list:
    #         msg += remove_other(join_clan, True)
    return msg
