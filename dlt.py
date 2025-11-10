# -*- coding:utf-8 -*-
import re
import urllib
import time
import sys

# --------------- 配置区 ---------------

# 你的投注号码
MY_RED = ['06','07','08','09','17','25']
MY_BLUE = ['10','01']

# 推送通知 URL（替换为你自己的）
PUSH_URL = 'https://example.com/push?msg='

# -------------------------------------

def getHtml(url):
    """抓取网页源码"""
    html = urllib.urlopen(url)
    return html.read()

def parse_numbers(html):
    """解析开奖期号、红蓝球号码"""
    issue = re.findall(r'<dt>([0-9]\d*).*</dt>', html)
    reds = re.findall(r'<li class="redball">([0-9]\d*)</li>', html)
    blues = re.findall(r'<li class="blueball">([0-9]\d*)</li>', html)
    if len(issue) > 0 and len(reds) >= 5 and len(blues) >= 2:
        return issue[0], reds[:5], blues[:2]
    return None, [], []

def check_win(reds, blues):
    """根据大乐透官方规则判断中奖等级"""
    red_hit = len(set(MY_RED) & set(reds))
    blue_hit = len(set(MY_BLUE) & set(blues))

    if red_hit == 5 and blue_hit == 2:
        return "一等奖"
    elif red_hit == 5 and blue_hit == 1:
        return "二等奖"
    elif red_hit == 5 and blue_hit == 0:
        return "三等奖"
    elif red_hit == 4 and blue_hit == 2:
        return "四等奖"
    elif (red_hit == 4 and blue_hit == 1) or (red_hit == 3 and blue_hit == 2):
        return "五等奖"
    elif (red_hit == 4 and blue_hit == 0) or (red_hit == 2 and blue_hit == 2):
        return "六等奖"
    elif red_hit == 3 and blue_hit == 1:
        return "七等奖"
    elif (red_hit == 1 and blue_hit == 2) or (red_hit == 0 and blue_hit == 2):
        return "八等奖"
    else:
        return None

def send_push(message):
    """中奖后发送推送通知"""
    try:
        urllib.urlopen(PUSH_URL + urllib.quote(message))
        print "🎉 推送成功：", message
    except Exception as e:
        print "推送失败：", e

def main():
    print ">>> 正在获取大乐透最新开奖..."
    html = getHtml("http://zx.500.com/dlt/")
    issue, reds, blues = parse_numbers(html)

    if not issue:
        print "未获取到开奖数据"
        return

    print "最新期号:", issue
    print "开奖号码：红区", reds, "  蓝区", blues
    result = check_win(reds, blues)

    if result:
        msg = "大乐透中奖啦！期号：%s 奖项：%s 🎉" % (issue, result)
        print msg
        send_push(msg)
    else:
        print "本期未中奖。祝下次好运！"

if __name__ == '__main__':
    main()
