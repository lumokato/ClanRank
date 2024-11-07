from pcrclient import PCRClient
from json import load
import pandas as pd
from datetime import datetime

with open('account.json', encoding='utf-8') as fp:
    total = load(fp)

# import time
# import bilicompare
# import asyncio

BOSS_LIFE_LIST = [[6000000, 8000000, 10000000, 12000000, 15000000],
                  [6000000, 8000000, 10000000, 12000000, 15000000],
                  [12000000, 14000000, 17000000, 19000000, 22000000],
                  [22000000, 23000000, 27000000, 29000000, 31000000],
                  [145000000, 150000000, 175000000, 195000000, 210000000]]
BOSS_SCORE_MUTIPILE = [[1.2, 1.2, 1.3, 1.4, 1.5],
                       [1.6, 1.6, 1.8, 1.9, 2.0],
                       [2.0, 2.0, 2.4, 2.4, 2.6],
                       [3.5, 3.5, 3.7, 3.8, 4.0],
                       [3.5, 3.5, 3.7, 3.8, 4.0]]
LAP_UPGRADE = [4, 11, 31, 39]


def boss_status(score):
    lap = 1
    boss_id = 0
    ptr = 0
    while True:
        tmp = int(BOSS_LIFE_LIST[ptr][boss_id] * BOSS_SCORE_MUTIPILE[ptr][boss_id])
        if score < tmp:
            remaining = int(BOSS_LIFE_LIST[ptr][boss_id] - score / BOSS_SCORE_MUTIPILE[ptr][boss_id])
            return lap, boss_id + 1, remaining, ptr
        score -= tmp
        boss_id += 1
        if boss_id > 4:
            boss_id = 0
            lap += 1
            if ptr <= 3:
                if lap >= LAP_UPGRADE[ptr]:
                    ptr += 1


def process_data(temp):
    if 'rank' not in temp:
        temp['rank'] = -1
    if 'damage' not in temp:
        temp['damage'] = 0
    if 'clan_name' not in temp:
        temp['clan_name'] = '此行会已解散'
    if 'member_num' not in temp:
        temp['member_num'] = 0
    if 'leader_name' not in temp:
        temp['leader_name'] = 'unknown'
    if 'grade_rank' not in temp:
        temp['grade_rank'] = 0
    return temp


class ClanBattle:
    def __init__(self, viewer_id, uid, access_key):
        self.uid = uid
        self.access_key = access_key
        self.Client = PCRClient(viewer_id)
        self.Client.login(uid, access_key)
        self.clan_id = 54

    def get_page_status(self, page):
        temp = self.Client.callapi('clan_battle/period_ranking', {'clan_id': self.clan_id, 'clan_battle_id': -1, 'period': -1, 'month': 0, 'page': page, 'is_my_clan': 0, 'is_first': 1})
        if 'period_ranking' not in temp:
            self.Client.login(self.uid, self.access_key)
            temp = self.Client.callapi('clan_battle/period_ranking', {'clan_id': self.clan_id, 'clan_battle_id': -1, 'period': -1, 'month': 0, 'page': page, 'is_my_clan': 0, 'is_first': 1})
        return temp['period_ranking']

    def get_rank_status(self, rank):
        temp1 = self.get_page_status((rank - 1) // 10)
        if (rank - 1) % 10 < len(temp1):
            temp = temp1[(rank - 1) % 10]
        else:
            temp = {}
        return process_data(temp)

    def get_page_data(self, page):
        temp1 = self.get_page_status(page)
        for i in range(0, len(temp1)):
            temp1[i] = process_data(temp1[i])
            lap, boss_id, remain, ptr = boss_status(temp1[i]['damage'])
            temp1[i]['lap'] = lap
            temp1[i]['boss_id'] = boss_id
            temp1[i]['remain'] = remain
            temp1[i]['ptr'] = ptr
        return temp1

    def rank_to_string(self, status, long_info=False):
        lap, boss_id, remaining = boss_status(status['damage'])

        if long_info:
            return '第{}名：{}，会长：{}，成员数：{}/30，分数：{}，当前进度：{}周目{}王，剩余血量：{}/{}，上期排名：{}'.format(status['rank'], status['clan_name'].replace('\r', ''), status['leader_name'].replace('\r', ''), status['member_num'], status['damage'], lap, boss_id, remaining, BOSS_LIFE_LIST[boss_id - 1], status['grade_rank'])
        else:
            return '第{}名：{}，分数：{}，当前进度：{}周目{}王，剩余血量{}/{}'.format(status['rank'], status['clan_name'], status['damage'], lap, boss_id, remaining, BOSS_LIFE_LIST[boss_id - 1])


def stage_data(final=0):
    start_time = datetime.now()
    App = ClanBattle(total["clan_account"]["vid"], total["clan_account"]["uid"], total["access_key"])
    save_data = []
    for page in range(30 if not final else 300):
        try:
            temp = App.get_page_data(page)
            for status in temp:
                save_data.append([status['rank'], status['clan_name'].replace('\r', ''), status['leader_name'].replace('\r', ''), status['member_num'], status['damage'], status['lap'], status['boss_id'], status['remain'], status['grade_rank']])
            if not temp:
                break
        except Exception:
            continue
    df = pd.DataFrame(save_data)
    df.columns = ['rank', 'clan_name', 'leader_name', 'member_num', 'damage', 'lap', 'boss_id', 'remain', 'grade_rank']
    end_time = datetime.now()
    filename = str(end_time.strftime("%Y%m%d%H")) + str(int(int(end_time.strftime("%M"))/30)*30).zfill(2)
    df.to_csv('qd/1/'+filename+'.csv')
    print(end_time-start_time)

    # async def add_score_list(sem, page):
    #     async with sem:
    #         score_list = []
    #         retry = 0
    #         while retry < 4:
    #             # print('查询'+str(page))
    #             page_data = await bilicompare.bilipage(page)
    #             if not page_data:
    #                 retry += 1
    #                 # time.sleep(1)
    #                 # continue
    #             else:
    #                 try:
    #                     for clan in page_data:
    #                         score_list.append(clan['damage'])
    #                     return score_list
    #                 except Exception:
    #                     retry += 1
    #                     # time.sleep(1)
    #                     # continue
    # score_list = []

    # async def score_main():
    #     sem = asyncio.Semaphore(8)
    #     tasks = []
    #     for page in range(55 if not final else 210):
    #         task = asyncio.create_task(add_score_list(sem, page))
    #         tasks.append(task)
    #     await asyncio.gather(*tasks)
    #     for i in tasks:
    #         if i._result:
    #             score_list.extend(i._result)
    #         else:
    #             # print('add0')
    #             score_list.extend([score_list[-1] if score_list else 0]*100)
    # b服数据对比
    # try:
    #     # loop = asyncio.get_event_loop()
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     loop.run_until_complete(score_main())

    #     qd_score_list = df['damage'].to_list()
    #     rank_list = []
    #     for score in qd_score_list:
    #         rank_list.append(bilicompare.binarySearch(score_list, 0, len(score_list)-1, score))

    #     df.insert(loc=len(df.columns), column='bili_rank', value=rank_list)
    # except Exception:
    #     time.sleep(1)
    # df.to_csv('qd/1/'+filename+'.csv')
    # bili_time = datetime.now()
    # print(end_time-start_time, bili_time-end_time)


if __name__ == '__main__':
    stage_data(1)
