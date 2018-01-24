import re
import json
from mitmproxy import ctx
from urllib.parse import quote
import string
import requests
import csv

neg_words = ['不包括', '哪个不是', '不属于', '哪一位不是', '不相等', '无法直接', '不能听到', '不需要', '不是以']

questions_map = {}
with open("questiuon_options_answer.csv", 'r', encoding="utf-8") as f:
    f_csv_read = csv.reader(f)
    for line in f_csv_read:
        if len(line) == 3:
            questions_map[line[0]] = line[2]


def response(flow):
    path = flow.request.path
    if path == '/question/bat/findQuiz':
        data = json.loads(flow.response.text)
        question = data['data']['quiz']
        options = data['data']['options']
        ctx.log.info('question : %s, options : %s'%(question, options))
        options = ask(question, options)
        data['data']['options'] = options
        flow.response.text = json.dumps(data)


def ask(question, options):
    if question in questions_map:
        options[options.index(questions_map[question])] += " √True"
        return options
    url = quote('https://www.baidu.com/s?wd=' + question, safe=string.printable)
    # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G9350 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/043806 Mobile Safari/537.36 MicroMessenger/6.6.1.1220(0x26060135) NetType/WIFI Language/zh_CN"}
    content = requests.get(url, headers=headers).text
    counts = []
    for option in options:
        count = content.count(option)
        ctx.log.info('option : %s, count : %s'%(option, count))
        counts.append(count)
    max_index = counts.index(max(counts))
    min_index = counts.index(min(counts))
    if any(word in question for word in neg_words):
        with open("questiuon_options_answer.csv", 'a', encoding='utf-8', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow([question, options, options[min_index]])
        options[min_index] += " √True"
    else:
        with open("questiuon_options_answer.csv", 'a', encoding='utf-8', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow([question, options, options[max_index]])
        options[max_index] += " √True"
    return options

