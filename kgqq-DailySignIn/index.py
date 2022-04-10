import json
import os

import requests

from API import *


def send(content, url=None):
    send_msg = 'https://gitee.com/hollc/code/raw/master/utils/send_msg.py'
    exec(requests.get(send_msg, headers={'User-Agent': 'edge', 'referer': 'gitee.com'}).text)


# 获取用户信息
def get_UserInfo(cookies):
    response = requests.get(get_UserInfo_url % cookies['uid'], cookies=cookies).json()
    return response['data']['profile.getProfile']['uFlowerNum']  # 返回当前鲜花数


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


# 每日签到
def singin(cookies):
    for t_iShowEntry in ['1', '2', '4', '16', '128', '512']:
        response = requests.get(singin_url % (cookies['uid'], t_iShowEntry), cookies=cookies).json()
        if response['data']['task.signinGetAward']['total'] == 1:
            awards = response['data']['task.signinGetAward']['awards']
            print('签到获得%d朵鲜花' % int(awards['num']))


# 批量执行所有领花函数
def do_task(cookies):
    singin(cookies)
    lottery(cookies)
    lottery0(cookies)
    lottery7(cookies)


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
