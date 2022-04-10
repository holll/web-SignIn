import json
import os
import platform
import re
import time

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()
timeout = 15
os.environ['uid'] = 'YangYiFan'
system = platform.system()

# 占位代码
BeautifulSoup('', 'html.parser')
time.sleep(0)
re.search('', '')
# 占位结束
headers = {
    'user-agent': 'edg'
}


def send(content, url=None):
    headers['referer'] = 'gitee.com'
    send_msg = 'https://gitee.com/hollc/code/raw/master/utils/send_msg.py'
    exec(requests.get(send_msg, headers=headers).text)


class web:
    count = 0

    def __init__(self, name, url, cookie, method, data, params, cmd, extra):
        self.name = name
        self.url = url
        print(cookie)
        self.cookie = json.loads(cookie.replace("'", '"')) if len(cookie) != 0 else ''
        self.method = method
        self.data = json.loads(data.replace("'", '"')) if data is not None else None
        self.params = json.loads(params.replace("'", '"')) if params is not None else None
        self.extra = extra if extra is not None else None
        self.cmd = cmd
        self.info = ''
        web.count += 1

    def __str__(self):
        # print(self.name)
        print(self.data)
        print(self.params)
        # print(self.extra)

    def my_requests(self):
        if self.method == 'get':
            response = requests.get(self.url, headers=headers, cookies=self.cookie, params=self.params,
                                    timeout=timeout, verify=False)
        elif self.method == 'post':
            response = requests.post(self.url, headers=headers, cookies=self.cookie, params=self.params,
                                     data=self.data, timeout=timeout, verify=False)
        else:
            print('requests方法错误' + self.method)
            response = None
        return response

    def run(self):
        try:
            response = self.my_requests()
            if system == 'Windows':
                print(response.content.decode('utf-8'))
            if self.extra is not None:
                exec(self.extra)
                response = eval('rep')
        except Exception as e:
            print('错误类型是', e.__class__.__name__)
            print('错误明细是', e)
            self.info = self.name + '：签到异常'
            print(self.info)
            return 0
        try:
            self.info = eval(self.cmd)
        except Exception as e:
            print('错误类型是', e.__class__.__name__)
            print('错误明细是', e)
            self.info = self.name + '：代码异常'
            print(response.text)
        print(self.info)


def main_handler(event, context):
    def is_default(__, parma):
        if __[parma]:
            locals()[parma] = __[parma]
        else:
            locals()[parma] = None
        return locals()[parma]

    desc = ''
    with open('./config.json', encoding='utf-8') as f:
        data = json.load(f)
    i = 1
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
    print('共载入%d个网站' % web.count)
    delay = 1
    i = 0
    for j in range(web.count):
        locals()['s' + str(j + 1)].run()
    print('签到完成')
    for j in range(web.count):
        desc = desc + locals()['s' + str(j + 1)].info + '\n'
        del locals()['s' + str(j + 1)]
    send(desc)


if __name__ == '__main__':
    main_handler(1, 1)