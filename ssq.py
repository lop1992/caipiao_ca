# -*- coding:utf-8 -*-
import re
import urllib2
import time
import sys

# -------------------- 配置 --------------------
datapath = sys.path[0]
datasuffix = 'txt'
if len(sys.argv) > 1:
    datapath = sys.argv[1]
    datasuffix = sys.argv[2]

# 你的固定号码（和大乐透一致）
my_numbers = {
    'red': ['06','07','08','09','17','25'],  # 红球 6 个
    'blue': ['10','01']                       # 蓝球 2 个（对应大乐透后区）
}

# 中奖消息推送 URL
push_url = "http://your_push_api.com/send?msg=你中奖了"

# -------------------- 获取网页 --------------------
def getHtml(url):
    response = urllib2.urlopen(url)
    return response.read()

html = getHtml("http://zx.500.com/ssq/")

# -------------------- 正则解析 --------------------
regs = [
    r'<dt>([0-9]\d*).*</dt>',                # 期号
    r'<li class="redball">([0-9]\d*)</li>',  # 红球
    r'<li class="blueball">([0-9]\d*)</li>'  # 蓝球
]

results = []
for reg in regs:
    pattern = re.compile(reg)
    rs = re.findall(pattern, html)
    results.append(rs)

# -------------------- 解析最新一期 --------------------
if len(results) == 3:
    issue = results[0][0]        # 最新期号
    red_balls = results[1][:6]   # 前6个红球
    blue_balls = results[2][:2]  # 前2个蓝球（大乐透后区）
    latest_numbers = {
        'red': red_balls,
        'blue': blue_balls
    }
    outstr = issue + ":" + ",".join(red_balls) + "/" + ",".join(blue_balls)

# -------------------- 保存到文件 --------------------
with open(datapath + '/lot_500_ssq.' + datasuffix, 'a') as f:
    f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " " + outstr + "\n")

# -------------------- 检查是否中奖 --------------------
def check_win(my_nums, draw_nums):
    red_match = len(set(my_nums['red']) & set(draw_nums['red']))
    blue_match = len(set(my_nums['blue']) & set(draw_nums['blue']))
    return red_match, blue_match

red_hit, blue_hit = check_win(my_numbers, latest_numbers)

# 中奖条件判断（可自行根据大乐透规则扩展）
if red_hit == 5 and blue_hit == 2:
    msg = "恭喜，中得一等奖！"
    print(msg)
    try:
        urllib2.urlopen(push_url)
    except Exception as e:
        print("推送失败:", e)
elif red_hit == 5 and blue_hit == 1:
    msg = "二等奖，红球5个+蓝球1个"
    print(msg)
    try:
        urllib2.urlopen(push_url)
    except Exception as e:
        print("推送失败:", e)
else:
    print("未中奖：红球匹配%d个, 蓝球匹配%d个" % (red_hit, blue_hit))
