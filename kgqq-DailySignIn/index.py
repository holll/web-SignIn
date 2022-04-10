import json
import os
import time

import requests

from API import *


def send(content, url=None):
    send_msg = 'https://gitee.com/hollc/code/raw/master/utils/send_msg.py'
    exec(requests.get(send_msg, headers={'User-Agent': 'edge', 'referer': 'gitee.com'}).text)


# 获取用户信息
def get_UserInfo(cookies):
    response = requests.get(get_UserInfo_url % cookies['uid'], cookies=cookies).json()
    return response['data']['profile.getProfile']['uFlowerNum']  # 返回当前鲜花数


# 每日签到
def singin(cookies):
    for t_iShowEntry in ['1', '2', '4', '16', '128', '512']:
        response = requests.get(singin_url % (cookies['uid'], t_iShowEntry), cookies=cookies).json()
        if response['data']['task.signinGetAward']['total'] == 1:
            awards = response['data']['task.signinGetAward']['awards'][0]
            print(awards)
            print('签到获得%d朵鲜花' % int(awards['num']))


# 每日抽奖
def lottery(cookies):
    for t_type in ['1', '2']:
        response = requests.get(lottery_url % (cookies['uid'], t_type), cookies=cookies).json()
        if response['data']['task.getLottery']['total'] == 1:
            awards = response['data']['task.getLottery']['awards']
            print('抽奖获得%d个%s' % (int(awards['num']), awards['desc']))


# 7日签到抽奖
def lottery7(cookies):
    response = requests.get(lottery7_url % (cookies['uid']), cookies=cookies).json()
    if response['data']['task.getLottery']['total'] == 1:
        awards = response['data']['task.getLottery']['awards']
        print('抽奖获得%d个%s' % (int(awards['num']), awards['desc']))


# 不明抽奖
def lottery0(cookies):
    response = requests.get(lottery7_url % (cookies['uid']), cookies=cookies).json()
    if response['data']['task.getLottery']['total'] == 1:
        awards = response['data']['task.getLottery']['awards']
        print('抽奖获得%d个%s' % (int(awards['num']), awards['desc']))


# 音乐邮局
def music_post_office(cookies):
    params = {
        'ns': 'proto_music_station',
        'cmd': 'message.get_reward',
        'mapExt': 'JTdCJTIyY21kTmFtZSUyMiUzQSUyMkdldFJld2FyZFJlcSUyMiUyQyUyMmZpbGUlMjIlM0ElMjJwcm90b19tdXNpY19zdGF0aW9uSmNlJTIyJTJDJTIyd25zRGlzcGF0Y2hlciUyMiUzQXRydWUlN0Q',
        't_uUid': cookies['uid']
    }
    for g_tk_openkey in range(16):
        response = requests.get(url=post_office_url % (cookies['uid'], g_tk_openkey), cookies=cookies)
        if response.json()['code'] == 1000:
            print(response.json()['msg'])
            return response.json()['msg']
        vct_music_cards = response.json()['data']['message.batch_get_music_cards']['vctMusicCards']
        vct_music_cards_list = sorted(vct_music_cards, key=lambda x: x["stReward"]["uFlowerNum"], reverse=True)[0]
        ugc_id = vct_music_cards_list["strUgcId"]
        key = vct_music_cards_list["strKey"]
        u_flower_num = vct_music_cards_list["stReward"]["uFlowerNum"]
        if u_flower_num > 10:
            json_data = '{"uInteractiveType":1,"uRewardType":0,"uFlowerNum":15}'
        elif 1 < u_flower_num < 10:
            json_data = '{"uInteractiveType":0,"uRewardType":0,"uFlowerNum":10}'
        else:
            json_data = None
            print('u_flower_num:%d' % u_flower_num)
        params['t_strKey'] = key
        params['t_strUgcId'] = ugc_id
        params['t_stReward:object'] = json_data
        requests.get(URL, params=params, cookies=cookies)
        time.sleep(0.5)


# 批量执行所有领花函数
def do_task(cookies):
    singin(cookies)
    time.sleep(1)
    lottery(cookies)
    time.sleep(1)
    lottery0(cookies)
    time.sleep(1)
    lottery7(cookies)
    time.sleep(1)
    music_post_office(cookies)


def main(event, context):
    # 读取配置文件，初始化所有账号
    with open('./config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    # 设置环境变量uid，提供给send函数读取
    os.environ['uid'] = config['uid']
    old_num = get_UserInfo(config['cookies'])
    do_task(config['cookies'])
    new_num = get_UserInfo(config['cookies'])
    send('获得%d朵鲜花，账户总计%d朵鲜花' % ((new_num - old_num), new_num))


if __name__ == '__main__':
    main(1, 1)
