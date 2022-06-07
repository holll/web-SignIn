import base64
import json
import logging
import os
import platform
import time

import requests

from API import *

# log格式
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# 配置文件路径
config_path = './config.json'
if platform.system() == 'Linux':
    config_path = '/www/wwwroot/download/conf/kgqq.json'

webapi = 'http://api.hollc.top/'


def send(content, url=None):
    t = int(time.time())
    parmas = {
        'key': 'aword2020',
        'uid': os.getenv('uid'),
        'content': content,
        'url': url,
        't': t,
        'saltKey': generate_salt_key('aword2020', t)
    }
    rep = requests.post(webapi + 'send', data=parmas).json()
    if rep['code'] != 200:
        logging.error(rep['msg'])

def generate_salt_key(_key, _t):
    temp_key = _key + str(_t)
    for i in range(5):
        temp_key = base64.b32encode(temp_key[:10].encode('utf-8')).decode('utf-8')
    return temp_key[-11:]


# 获取用户信息
def get_userinfo(cookies):
    response = requests.get(get_UserInfo_url % cookies['uid'], cookies=cookies).json()
    logging.debug('get_userinfo:' + str(response))
    time.sleep(0.5)
    return response['data']['profile.getProfile']['uFlowerNum']  # 返回当前鲜花数


# 每日签到
def singin(cookies):
    for t_iShowEntry in ['1', '2', '4', '16', '128', '512']:
        response = requests.get(singin_url % (cookies['uid'], t_iShowEntry), cookies=cookies).json()
        time.sleep(0.5)
        logging.debug('singin:' + str(response))
        if response['code'] == 0 and response['data']['task.signinGetAward']['total'] == 1:
            awards = response['data']['task.signinGetAward']['awards'][0]
            logging.debug(awards)
            logging.info('签到获得%d朵鲜花' % int(awards['num']))


# 每日抽奖
def lottery_d(cookies):
    for t_type in ['1', '2']:
        response = requests.get(lottery_url % (cookies['uid'], t_type), cookies=cookies).json()
        logging.debug('lottery_d:' + str(response))
        time.sleep(0.5)
        if response['code'] == 0 and response['data']['task.getLottery']['total'] == 1:
            awards = response['data']['task.getLottery']['awards']
            logging.info('抽奖获得%d个%s' % (int(awards['num']), awards['desc']))


def lottery(url, cookies):
    response = requests.get(url % (cookies['uid']), cookies=cookies).json()
    logging.debug('lottery:' + str(response))
    time.sleep(0.5)
    if response['code'] == 0 and response['data']['task.getLottery']['total'] == 1:
        awards = response['data']['task.getLottery']['awards']
        logging.info('抽奖获得%d个%s' % (int(awards['num']), awards['desc']))


# 音乐邮局
def music_post_office(cookies):
    params = {
        'ns': 'proto_music_station',
        'cmd': 'message.get_reward',
        'mapExt': 'JTdCJTIyY21kTmFtZSUyMiUzQSUyMkdldFJld2FyZFJlcSUyMiUyQyUyMmZpbGUlMjIlM0ElMjJwcm90b19tdXNpY19zdGF0aW9uSmNlJTIyJTJDJTIyd25zRGlzcGF0Y2hlciUyMiUzQXRydWUlN0Q',
        't_uUid': cookies['uid']
    }
    for g_tk_openkey in range(16):
        response = requests.get(url=post_office_url % (cookies['uid'], g_tk_openkey), cookies=cookies).json()
        logging.debug('music_post_office:' + str(response))
        time.sleep(0.5)
        if response['code'] == 1000:
            logging.debug(response['msg'])
            return response['msg']
        vct_music_cards = response['data']['message.batch_get_music_cards']['vctMusicCards']
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
            logging.debug('u_flower_num:%d' % u_flower_num)
        params['t_strKey'] = key
        params['t_strUgcId'] = ugc_id
        params['t_stReward:object'] = json_data
        requests.get(URL, params=params, cookies=cookies)
        time.sleep(0.5)


# 批量执行所有领花函数
def do_task(cookies):
    singin(cookies)
    time.sleep(1)
    lottery_d(cookies)
    time.sleep(1)
    lottery(lottery7_url, cookies)
    time.sleep(1)
    lottery(lottery0_url, cookies)
    time.sleep(1)
    music_post_office(cookies)


def main(event, context):
    # 读取配置文件，初始化所有账号
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    # 设置环境变量uid，提供给send函数读取
    os.environ['uid'] = config['uid']
    i = 0
    for cookie in config['cookies']:
        old_num = get_userinfo(cookie)
        do_task(cookie)
        new_num = get_userinfo(cookie)
        send('用户%d获得%d朵鲜花，账户总计%d朵鲜花' % (i + 1, new_num - old_num, new_num))
        i += 1


if __name__ == '__main__':
    main(1, 1)
