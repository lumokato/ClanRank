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
    for clan in total["clan"]:
        if clan["clan_id"] == clan_id:
            farm_account = clan["account"]
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


def user_clear(qq, vid, clear_type):
    req_time = time.time()
    user_type = 'none'
    for user_index in total["users"].keys():
        if str(total["users"][user_index]["qq"]) == qq:
            find_index = user_index
            viewer_id = total["users"][user_index]["vid"]
            join_clan = total["users"][user_index]["join_clan"]
            if str(viewer_id)[-4:] == vid or str(viewer_id) == vid:
                user_type = 'user'
            if isinstance(total["users"][user_index]["qq"], str):
                user_type = 'admin'
    msg = "输入错误"
    if user_type == 'user' and clear_type == 'clean':
        if int(req_time) - int(total["users"][find_index]["last_clean_time"]) > 1800:
            # msg = '调用remove_other()'+str(join_clan)
            msg = remove_other(join_clan)
            total["users"][find_index]["last_clean_time"] = req_time
            save_total()
        else:
            msg = '操作间隔小于30分钟'
    elif user_type == 'user' and clear_type == 'remove':
        if int(req_time) - int(total["users"][find_index]["last_clear_time"]) > 1800:
            # msg = '调用remove_user()' + str(join_clan)+str(viewer_id)
            msg = remove_user(join_clan, viewer_id)
            total["users"][find_index]["last_clear_time"] = req_time
            save_total()
        else:
            msg = '操作间隔小于30分钟'
    elif user_type == 'admin' and clear_type == 'clean':
        for clan in total["clan"]:
            if str(clan["clan_id"]) == vid:
                # msg = '调用remove_other()' + vid
                msg = remove_other(clan["clan_id"], True)
                total["users"]["0"]["last_clear_time"] = req_time
                save_total()
    elif user_type == 'admin' and clear_type == 'remove':
        for user_index in total["users"].keys():
            if str(total["users"][user_index]["vid"]) == vid:
                join_clan = total["users"][user_index]["join_clan"]
                # msg = '调用remove_user()' + str(join_clan)+str(vid)
                msg = remove_user(join_clan, vid)
                total["users"]["0"]["last_clean_time"] = req_time
                save_total()
    elif user_type != 'none' and clear_type == 'clan':
        for clan in total["clan"]:
            if clan["clan_id"] == join_clan:
                msg = '工会名：' + clan["name"]

    return msg
