# -*- coding:utf-8 -*-
import re
import urllib
import time
import sys
import requests  # 用于推送中奖通知

# ===================== 配置 =====================
datapath = sys.path[0]
datasuffix = 'txt'
my_ticket = {
    'red': ['06','07','08','09','17','25'],  # 你的红球号码
    'blue': ['10','01']                      # 你的蓝球号码
}
push_url = "http://your_push_url_here"      # 中奖通知URL

if len(sys.argv) > 1:
    datapath = sys.argv[1]
    datasuffix = sys.argv[2]

# ===================== 获取网页 =====================
def getHtml(url):
    html = urllib.urlopen(url)
    return html.read()

html = getHtml("http://zx.500.com/ssq/")

# ===================== 正则抓取开奖号码 =====================
reg = ['<dt>([0-9]\d*).*</dt>']                   # 期号
reg.append('<li class="redball">([0-9]\d*)</li>') # 红球
reg.append('<li class="blueball">([0-9]\d*)</li>')# 蓝球

outstr = ""
results = []

for i in range(len(reg)):
    page = re.compile(reg[i])
    rs = re.findall(page, html)
    results.append(rs)
    for j in range(len(rs)):
        outstr += rs[j] + ","

period = results[0][0]          # 最新期号
red_nums = results[1][:6]       # 最新红球
blue_nums = results[2][:1]      # 最新蓝球

# ===================== 写入本地记录 =====================
with open(datapath+'/lot_500_ssq.'+datasuffix, 'a') as f:
    f.write(time.strftime('%Y-%m-%d',time.localtime(time.time()))+":"+period+":"+",".join(red_nums)+"/"+",".join(blue_nums)+'\n')

# ===================== 判断中奖等级 =====================
def check_prize(my_ticket, draw):
    my_red = set(my_ticket['red'])
    my_blue = set(my_ticket['blue'])
    draw_red = set(draw['red'])
    draw_blue = set(draw['blue'])

    red_hit = len(my_red & draw_red)
    blue_hit = len(my_blue & draw_blue)

    # 双色球最新官方规则
    prize = None
    if red_hit == 6 and blue_hit == 1:
        prize = "一等奖"
    elif red_hit == 6 and blue_hit == 0:
        prize = "二等奖"
    elif red_hit == 5 and blue_hit == 1:
        prize = "三等奖"
    elif (red_hit == 5 and blue_hit == 0) or (red_hit == 4 and blue_hit == 1):
        prize = "四等奖"
    elif (red_hit == 4 and blue_hit == 0) or (red_hit == 3 and blue_hit == 1):
        prize = "五等奖"
    elif blue_hit == 1 or (red_hit <= 2 and blue_hit == 1):
        prize = "六等奖"

    return prize

draw = {'red': red_nums, 'blue': blue_nums}
prize = check_prize(my_ticket, draw)

# ===================== 中奖推送 =====================
if prize:
    message = "恭喜！你在双色球期号{}中奖，奖级：{}，开奖号码：红球{} 蓝球{}".format(period, prize, ",".join(red_nums), ",".join(blue_nums))
    print(message)
    # 调用推送 URL
    try:
        requests.get(push_url, params={'msg': message})
    except Exception as e:
        print("推送失败:", e)
else:
    print("未中奖，本期双色球号码：红球{} 蓝球{}".format(",".join(red_nums), ",".join(blue_nums)))
