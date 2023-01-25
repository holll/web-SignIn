import hashlib
import json
import logging
import os
import platform
import re
import time

import requests
import urllib3
from bs4 import BeautifulSoup

# 忽略警告
urllib3.disable_warnings()
# 部分网站服务器在国外，为避免长时间无响应，设定最大超时时间
timeout = 15
system = platform.system()
# log格式
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# 配置文件路径
config_path = './config.json'
if platform.system() == 'Linux':
    config_path = '/www/wwwroot/download/conf/web-sign.json'
# 部分代码在exec函数中执行，因此主文件会显示未使用的import
BeautifulSoup('', 'html.parser')
time.sleep(0)
re.search('', '')
# 占位结束

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
    def get_md5(s):
        hl = hashlib.md5()
        hl.update(s.encode('utf8'))
        return hl.hexdigest()

    temp_key = _key + str(_t)
    return get_md5(temp_key)[-11:]


class web:
    count = 0

    def __init__(self, name, url, cookie, headers, method, data, params, cmd, extra):
        self.name = name
        self.url = url
        self.cookie = json.loads(cookie.replace("'", '"')) if len(cookie) != 0 else ''
        self.headers = json.loads(headers.replace("'", '"')) if headers is not None else None
        self.method = method
        self.data = json.loads(data.replace("'", '"')) if data is not None else None
        self.params = json.loads(params.replace("'", '"')) if params is not None else None
        self.extra = extra if extra is not None else None
        self.cmd = cmd
        self.info = ''
        web.count += 1

    def __str__(self):
        # logging.debug(self.name)
        logging.debug(self.data)
        logging.debug(self.params)
        logging.debug(self.headers)
        # logging.debug(self.extra)

    def my_requests(self):
        if self.method == 'get':
            response = requests.get(self.url, headers=self.headers, cookies=self.cookie, params=self.params,
                                    timeout=timeout, verify=False)
        elif self.method == 'post':
            response = requests.post(self.url, headers=self.headers, cookies=self.cookie, params=self.params,
                                     data=self.data, timeout=timeout, verify=False)
        else:
            logging.warning('requests方法错误' + self.method)
            response = None
        return response

    def run(self):
        try:
            response = self.my_requests()
            if system == 'Windows':
                logging.debug(response.content.decode('gbk'))
            else:
                logging.debug(response.text)
            if self.extra is not None:
                time.sleep(1)
                exec(self.extra)
                response = eval('rep')
        except Exception as e:
            logging.error('错误类型是', e.__class__.__name__)
            logging.error('错误明细是', e)
            self.info = self.name + '：签到异常'
            logging.error(self.info)
            return 0
        try:
            self.info = eval(self.cmd)
        except Exception as e:
            logging.error('错误类型是', e.__class__.__name__)
            logging.error('错误明细是', e)
            logging.error('错误代码是', self.cmd)
            self.info = self.name + '：代码异常'
            logging.error(response.text)
        logging.info(self.info)


def main_handler(event, context):
    def is_default(__, parma):
        if __[parma]:
            locals()[parma] = __[parma]
        else:
            locals()[parma] = None
        return locals()[parma]

    desc = ''
    error_msg = ''
    with open(config_path, encoding='utf-8') as f:
        data = json.load(f)
    i = 1
    os.environ['uid'] = data['uid']
    for _ in data['web']:
        name = _['name']
        url = _['url']
        cookie = _['cookie']
        method = _['method']
        cmd = _['exec']
        _.setdefault('extra', False)
        _.setdefault('parmas', False)
        _.setdefault('data', False)
        _.setdefault('headers', False)
        locals()['s' + str(i)] = web(name, url, cookie, is_default(_, 'headers'), method, is_default(_, 'data'),
                                     is_default(_, 'parmas'), cmd, is_default(_, 'extra'))
        i += 1
    logging.info('共载入%d个网站' % web.count)
    delay = 1
    i = 0
    for j in range(web.count):
        locals()['s' + str(j + 1)].run()
    logging.info('签到完成')
    for j in range(web.count):
        if '异常' in locals()['s' + str(j + 1)].info:
            error_msg = error_msg + locals()['s' + str(j + 1)].info + '\n'
        else:
            desc = desc + locals()['s' + str(j + 1)].info + '\n'
        del locals()['s' + str(j + 1)]
    if len(desc) != 0:
        send(desc)
    if len(error_msg) != 0:
        send(error_msg)


if __name__ == '__main__':
    main_handler(1, 1)
