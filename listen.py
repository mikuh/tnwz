import os
import json
from mitmproxy import ctx
from urllib.parse import quote
import string
import requests
import sqlite3
import hashlib

conn = sqlite3.connect('qa.db')
cursor = conn.cursor()

# xy = ['538 1043', '560 1229', '540 1430', '543 1616']

neg_words = ['不包括', '哪个不是', '不属于', '哪一位不是', '不相等', '无法直接', '不能听到', '不需要', '不是以']

questions_map = {}
cursor.execute('select question, answer from qa')
for row in cursor.fetchall():
    questions_map[row[0]] = row[1]


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
        options[options.index(questions_map[question].strip())] += "【True】"
        return options
    url = quote('https://www.baidu.com/s?wd=' + question, safe=string.printable)
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
    content = requests.get(url, headers=headers).text
    counts = []
    for option in options:
        count = content.count(option)
        ctx.log.info('option : %s, count : %s'%(option, count))
        counts.append(count)
    max_index = counts.index(max(counts))
    min_index = counts.index(min(counts))
    flag = any(word in question for word in neg_words)

    try:
        hash_question = hashlib.sha1(question.encode('utf-8')).hexdigest()
        cursor.execute("INSERT INTO qa (hash_question, question, options, answer) VALUES (?, ?, ?, ? )",
                       (hash_question, question, str(options), options[min_index] if flag else options[max_index]))
        conn.commit()
        if flag:
            options[min_index] += "【True】"
        else:
            options[max_index] += "【True】"
    except Exception as e:
        print(e)
    return options

