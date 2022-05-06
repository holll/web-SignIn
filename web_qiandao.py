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

# Todo 部分网站要求cookie与user-agent匹配 放在config中自定义
headers = {
    'user-agent': 'edg'
}

webapi = 'http://49.234.133.60:8888/'


def send(content, url=None):
    parmas = {
        'key': 'aword2020',
        'uid': os.getenv('uid'),
        'content': content,
        'url': url
    }
    rep = requests.post(webapi + 'send', data=parmas).json()
    if rep['code'] != 200:
        logging.error(rep['msg'])


class web:
    count = 0

    def __init__(self, name, url, cookie, method, data, params, cmd, extra):
        self.name = name
        self.url = url
        self.cookie = json.loads(cookie.replace("'", '"')) if len(cookie) != 0 else ''
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
        # logging.debug(self.extra)

    def my_requests(self):
        if self.method == 'get':
            response = requests.get(self.url, headers=headers, cookies=self.cookie, params=self.params,
                                    timeout=timeout, verify=False)
        elif self.method == 'post':
            response = requests.post(self.url, headers=headers, cookies=self.cookie, params=self.params,
                                     data=self.data, timeout=timeout, verify=False)
        else:
            logging.warning('requests方法错误' + self.method)
            response = None
        return response

    def run(self):
        try:
            response = self.my_requests()
            if system == 'Windows':
                logging.debug(response.content.decode('utf-8'))
            else:
                logging.debug(response.text)
            if self.extra is not None:
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
        locals()['s' + str(i)] = web(name, url, cookie, method, is_default(_, 'data'), is_default(_, 'parmas'), cmd,
                                     is_default(_, 'extra'))
        i += 1
    logging.info('共载入%d个网站' % web.count)
    delay = 1
    i = 0
    for j in range(web.count):
        locals()['s' + str(j + 1)].run()
    logging.info('签到完成')
    for j in range(web.count):
        desc = desc + locals()['s' + str(j + 1)].info + '\n'
        del locals()['s' + str(j + 1)]
    send(desc)


if __name__ == '__main__':
    main_handler(1, 1)
