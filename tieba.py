# -*- coding: utf8 -*-
import base64
import logging
import time
from random import randint
from time import sleep

import os
import requests

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


def main(*args):
    sleep(randint(0, 10))
    # 数据
    like_url = 'https://tieba.baidu.com/mo/q/newmoindex?'
    sign_url = 'http://tieba.baidu.com/sign/add'
    tbs = '4fb45fea4498360d1547435295'
    head = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': 'BDUSS=k0N1NzWVZtbzRKcnczYmRNVHpIVmxxYTlFa1ZzSmRkOVpzRUFDQnVQaHkwSHBnRUFBQUFBJCQAAAAAAAAAAAEAAADmIa15Yml1X3BhX2JpdQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHJDU2ByQ1NgLU',
        'Host': 'tieba.baidu.com',
        'Referer': 'http://tieba.baidu.com/i/i/forum',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'}
    s = requests.Session()

    # 获取关注的贴吧
    bars = []
    dic = s.get(like_url, headers=head).json()['data']['like_forum']
    for bar_info in dic:
        bars.append(bar_info['forum_name'])

    # 签到
    already_signed_code = 1101
    success_code = 0
    need_verify_code = 2150040
    already_signed = 0
    succees = 0
    failed_bar = []
    n = 0
    sleep(randint(0, 10))

    while n < len(bars):
        sleep(0.5)
        bar = bars[n]
        data = {
            'ie': 'utf-8',
            'kw': bar,
            'tbs': tbs
        }
        try:
            r = s.post(sign_url, data=data, headers=head)
        except Exception as e:
            print(f'未能签到{bar}, 由于{e}。')
            failed_bar.append(bar)
            continue
        dic = r.json()
        msg = dic['no']
        if msg == already_signed_code:
            already_signed += 1
            r = '已经签到过了!'
        elif msg == need_verify_code:
            n -= 1
            r = '需要验证码，即将重试!'
        elif msg == success_code:
            r = f"签到成功!你是第{dic['data']['uinfo']['user_sign_rank']}个签到的吧友,共签到{dic['data']['uinfo']['total_sign_num']}天。"
        else:
            r = '未知错误!' + dic['error']
        print(f"{bar}：{r}")
        succees += 1
        n += 1
    l = len(bars)
    failed = "\n失败列表：" + '\n'.join(failed_bar) if len(failed_bar) else ''
    tdwt = f'''共{l}个吧，其中: {succees}个吧签到成功，{len(failed_bar)}个吧签到失败，{already_signed}个吧已经签到。{failed}'''
    send(tdwt)


if __name__ == '__main__':
    os.environ['uid'] = 'YangYiFan'
    main()
