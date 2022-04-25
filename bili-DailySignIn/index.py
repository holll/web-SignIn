import datetime
import json
import logging
import os
import platform
import time

import pytz
import requests

import API

UserAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'
# log格式
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# 配置文件路径
config_path = './config.json'
if platform.system() == 'Linux':
    config_path = '/www/wwwroot/download/conf/bilibili.json'


def send(content, url=None):
    send_msg = 'https://gitee.com/hollc/code/raw/master/utils/send_msg.py'
    exec(requests.get(send_msg, headers={'User-Agent': 'edge', 'referer': 'gitee.com'}).text)


class User:
    num = 0

    def __init__(self, daily_task, sign, charge, headers):
        self.daily_task = daily_task
        self.sign = sign
        self.need_charge = charge['date']
        self.charge_user = charge['user']
        self.mid = None
        self.S = requests.session()
        self.S.headers = headers
        User.num += 1

    # 获取用户信息
    def get_user_info(self):
        rep = self.S.get(API.user_info).json()
        if rep['code'] == 0:
            data = rep['data']
            level_info = data['level_info']

            userInfo = {
                'name': data['uname'],  # 用户名
                'mid': data['mid'],  # uid
                'level': level_info['current_level'],  # 等级
                'coins': data['money'],  # 硬币数
                'current_exp': level_info['current_exp'],
                'next_exp': level_info['next_exp'],
                'level_exp': '%d/%d' % (level_info['current_exp'], level_info['next_exp']),
                'vipType': data['vipType']
            }
            logging.debug(userInfo)
            return {'status': True, 'userInfo': userInfo}
        else:
            return {'status': False, 'message': rep['message']}

    # 每日看视频
    def watch_video(self, want_share):
        def get_timestamp():
            time_str = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")
            timestamp = int(time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S')))
            return timestamp

        # 分享视频
        def share_video(info):
            data = {'aid': info['aid'], 'csrf': os.getenv('bili_jct')}
            rep = self.S.post(API.video_share, data=data).json()
            if rep['code'] == 0:
                logging.info('分享视频[%s]成功' % info['title'])
                return '分享视频[%s]成功' % info['title']
            else:
                logging.info('分享视频[%s]失败,因为%s' % (info['title'], rep['message']))
                return '分享视频[%s]失败,因为%s' % (info['title'], rep['message'])

        # 从热门视频中选择需要观看的视频
        bvid = get_hot_video()
        timestamp = get_timestamp()
        info = get_video_info(bvid)
        # 开始播放视频
        data = {
            'aid': info['aid'],
            'bvid': bvid,
            'cid': info['cid'],
            'mid': os.getenv('DedeUserID'),
            'csrf': os.getenv('bili_jct'),
            'played_time': 0,
            'realtime': 0,
            'real_played_time': 0,
            'play_type': 1,
            'dt': 2,
            'type': 3,
            'auto_continued_play': 0,
            'start_ts': timestamp
        }
        logging.debug(data)
        # Todo 疑似接口有问题，暂不开启观看视频
        return 0
        rep = self.S.post(API.video_heartbeat, data=data).json()
        if want_share == 1:
            is_share = share_video(info)
        else:
            is_share = '不启用分享视频'
        if rep['code'] == 0:
            # 模拟看过视频
            time.sleep(5)
            data['played_time'] = data['realtime'] = data['real_played_time'] = info['duration'] - 1
            data['play_type'] = 0
            rep = self.S.post(API.video_heartbeat, data=data).json()
            if rep['code'] == 0:
                logging.info('观看视频成功')
                return '观看视频成功，' + is_share
            else:
                logging.info('观看视频失败')
                return '观看视频失败，' + is_share

    # 直播签到
    def live_broadcast_checkin(self):
        rep = self.S.get(API.live_sign).json()

        if rep['code'] == 0:
            # 签到成功
            data = rep['data']
            logging.info('直播签到成功，获得奖励:%s，%s，本月已签到%d/%d天' % (
                data['text'], data['specialText'], data['hadSignDays'], data['allDays']))
            return '直播签到成功，获得奖励:%s，%s，本月已签到%d/%d天' % (
                data['text'], data['specialText'], data['hadSignDays'], data['allDays'])
        else:
            logging.info('直播签到失败,因为%s' % rep['message'])
            return '直播签到失败,因为%s' % rep['message']

    # 漫画签到
    def comics_checkin(self):
        # 查看漫画签到信息
        def comics_checkin_info():
            rep = self.S.post(API.comics_info).json()
            if rep['code'] == 0:
                return {'status': True, 'day_count': rep['data']['day_count']}
            else:
                return {'status': False, 'message': rep['msg']}

        data = {'platform': 'android'}
        rep = self.S.post(API.comics_sign, data=data).json()
        if rep['code'] == 0:
            msg = '漫画签到成功，已经连续签到%d天' % comics_checkin_info()['day_count']
            logging.info(msg)
            return msg
        elif rep['code'] == 'invalid_argument':
            logging.info('漫画签到失败,因为重复签到了')
            return '漫画签到失败,因为重复签到了'

    def charge(self):
        # 获取B币券领取状态
        rep = self.S.get(API.free_Bb_info + '?csrf=' + os.getenv('bili_jct')).json()
        if rep['code'] == 0 and rep['data']['list'][0]['state'] == 0:
            # 有B币券，开始领取
            data = {
                'csrf': os.getenv('bili_jct'),
                'type': 1
            }
            rep = self.S.post(API.get_free_Bb, data=data).json()
            if rep['code'] == 0:
                logging.info('B币券领取成功，尝试充电')
                logging.debug(rep)
                if self.charge_user != -1:  # 指定充电用户uid，-1表示给自己充电
                    mid = self.charge_user
                else:
                    mid = self.mid
                data = {
                    'bp_num': 5,
                    'is_bp_remains_prior': 'true',
                    'up_mid': mid,
                    'otype': 'up',
                    'oid': mid,
                    'csrf': os.getenv('bili_jct')
                }
                rep = self.S.post(API.charge, data=data).json()
                logging.debug(rep)
                if rep['code'] == 0 and rep['data']['status'] == 4:
                    if self.charge_user == -1:
                        return '给自己充电5B币成功'
                    else:
                        return '给用户%s充电5B币成功' % mid
                else:
                    return rep['data']['msg']
            else:
                return 'B币券领取失败：' + rep['message']
        else:
            return '本月已领取B币券'

    def Inquire_exp(self):
        rep = self.S.get(API.daily_task_info).json()
        logging.debug(rep)
        if rep['code'] == 0:
            today_exp = 0
            if rep['data']['login']:
                today_exp += 5
            if rep['data']['watch']:
                today_exp += 5
            if rep['data']['share']:
                today_exp += 5
            rep = self.S.get(API.get_exp_count).json()
            today_exp += rep['number']
            return today_exp
        else:
            return -1

    # Todo 投币
    # def give_coin(p, want_coin_num, headers, csrf, coinnum=1, select_like=0):
    #     has_coin_num = 0  # 已经投币次数
    #     _list = {}
    #     for index, item in enumerate(p['video_list'].values()):
    #         data = {
    #             'aid': str(item['aid']),
    #             'multiply': coinnum,  # 每次投币多少个,默认 1 个
    #             'select_like': select_like,  # 是否同时点赞, 默认不点赞
    #             'cross_domain': 'true',
    #             'csrf': csrf
    #         }
    #         # 当已投币数超过想投币数时退出
    #         if has_coin_num < want_coin_num:
    #             rep = requests.post(API.add_coin, headers=headers, data=data).json()
    #             if rep['code'] == 0:
    #                 # 投币成功
    #                 print(f'给{item.get("title")}投币成功🎉🎉')
    #                 _list.update({index: {'status': True, 'title': item['title']}})
    #                 has_coin_num = has_coin_num + 1  # 投币次数加 1
    #             else:
    #                 # 投币失败
    #                 print('给[%s]投币失败😥😥,因为%s' % (item['title'], rep['message']))
    #                 _list.update({index: {'status': False, 'title': item['title']}})
    #         else:
    #             print('投币完成,正在退出')
    #             break
    #     return list

    def start(self):
        # 获取用户信息
        user = self.get_user_info()
        if user['status']:
            userInfo = user['userInfo']
            my_level = userInfo['level']
            my_coins = userInfo['coins']
            my_exp = userInfo['level_exp']
            content = f'等级：lv{my_level}\n硬币：{my_coins}\n经验：{my_exp}\n'
        else:
            content = 'Bilibili登录过期'
            send(content)
            return 0
        logging.info(content)

        msg = ''
        if self.daily_task['watch']:
            logging.info('正在观看视频...')
            msg += self.watch_video(self.daily_task['share']) + '\n'
        else:
            logging.info('不进行观看...')
            msg += '不进行观看视频...\n'
        if self.sign['live']:
            logging.info('正在进行直播签到...')
            msg += self.live_broadcast_checkin() + '\n'
        else:
            logging.info('不启用直播签到...')
            msg += '不启用直播签到...\n'
        if self.sign['comics']:
            logging.info('正在进行漫画签到...')
            msg += self.comics_checkin() + '\n'
        else:
            logging.info('不启用漫画签到...')
            msg += '不启用漫画签到...\n'
        if self.need_charge == -1:
            logging.info('未开启充电')
            msg += '未开启充电\n'
        elif self.need_charge == int(datetime.datetime.now(pytz.timezone('PRC')).strftime("%d")):
            logging.info('正在进行充电')
            msg += self.charge() + '\n'
        else:
            logging.info('未到充电日期%d号' % self.need_charge)
            msg += '未到充电日期%d号\n' % self.need_charge
        # 查询经验值
        today_exp = self.Inquire_exp()
        if today_exp != -1:
            today_exp = 10 if today_exp == 0 else today_exp
            is_exp = '今日获取经验值%d，升级预计还需%d天' % (
                today_exp, int((userInfo['next_exp'] - userInfo['current_exp']) / today_exp))
            logging.info(is_exp)
        else:
            is_exp = '未获取到今日经验值'
        msg += is_exp
        # 开始推送
        desp = content + '\n' + msg
        print('------开始推送------')
        send(desp)


# 获取视频信息
def get_video_info(bvid):
    rep = requests.get(API.video_info + '?bvid=' + bvid).json()
    if rep['code'] == 0:
        data = rep['data']
        video_info = {
            'aid': data['aid'],
            'bvid': data['bvid'],
            'duration': data['duration'],
            'cid': data['cid'],
            'title': data['title']
        }
        return video_info
    else:
        send('获取视频信息出错：' + rep['message'])
        return 0


# 获取热门视频
def get_hot_video():
    # rid是分区代码
    rid = '36'  # 知识区
    res = requests.get(API.hot_video + '?rid=' + rid).json()
    if res['code'] == 0:
        return res['data'][0]['bvid']
    else:
        logging.debug(res['message'])
        send('获取热门视频出错：' + res['message'])
        return 0


def main(event, context):
    # 读取配置文件，初始化所有账号
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    for user in config['users']:
        num = 1
        daily_task = user['daily_task']
        sign = user['sign']
        charge = user['charge']
        bili_cookie = 'DedeUserID=%s;DedeUserID__ckMd5=%s;SESSDATA=%s;bili_jct=%s' % (
            user['cookie']['DedeUserID'], user['cookie']['DedeUserID__ckMd5'], user['cookie']['SESSDATA'],
            user['cookie']['bili_jct'])
        os.environ['bili_jct'] = user['cookie']['bili_jct']
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'cookie': bili_cookie,
            'User-Agent': UserAgent
        }
        locals()['s' + str(num)] = User(daily_task, sign, charge, headers)
    for i in range(1, User.num + 1):
        locals()['s' + str(i)].start()


if __name__ == '__main__':
    main(1, 1)
