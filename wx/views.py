# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET

import hashlib
import random

# Create your views here.

TOKEN = "fishioon"

g_result = [
        '陪对方看喜欢的电影',
        '让对方撒娇，直到对方亲你',
        '特许你继续抽签2次', 
        '用10种不同的方式赞美对方',
        '让我咬一口',
        '包一件家务一周',
        '抱或者背对方走一圈',
        '表演一段钢管舞',
        '讲一段笑话',
        '亲手为对方做一顿饭',
        '请对方吃一顿大餐',
        '罚酒一杯',
        '给对方洗脚',
        '喂对方吃饭',
        '用扭腰写出对方要求的字',
        '哄我睡觉',
        '学猫猫卖萌，在对方身上撒娇',
        '让对方深情的唱一首情歌',
        '让对方当大马骑两分钟',
        '替对方按摩',
        '说99遍我爱你',
        '严肃的说我是猪',
        '让对方差遣一周',
        '说出对方喜欢的，并买给TA',
        '让对方咬一口 不许喊疼',
        '吃掉对方身上的事物残渣',
        '亲嘴10分钟',
        '让对方彩排结婚',
        '被对方挠痒痒不许躲',
        '表白到对方点头愿意为止'
        ]

@csrf_exempt
def wxapp(request):
    if request.method == "GET":
        return HttpResponse(check_signature(request))
    elif request.method == "POST":
        return HttpResponse(reply_msg(request))
    else:
        return HttpResponse("Not support http method") 

def check_signature(request):
    global TOKEN
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    echostr = request.GET.get("echostr",None)

    token = TOKEN
    tmplist = [token, timestamp, nonce]
    tmplist.sort()
    tmpstr = "%s%s%s" % tuple(tmplist)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        return echostr
    else:
        return "Check failed"

def get_help_msg(result):
    msg = ("欢迎使用爱情上上签，为你的TA求支签!\n"
            "使用说明：输入'sj'返回求签结果\n"
            "目前已有的签如下：\n")
    for i in range(0, len(result)):
        msg = msg + str(i) + ". " + result[i] + "\n"
    return msg

def reply_msg(request):
    global g_result
    msg = parse_msg(request.body)
    req_data = msg['Content']
    data = ""
    if msg['MsgType'] == 'text' and req_data.lower() == 'sj':
        data = g_result[random.randint(0, len(g_result)-1)]
    else:
        data = get_help_msg(g_result)
    return packet_msg(msg, data)

def parse_msg(request_body):
    msg = {}
    root = ET.fromstring(request_body)
    if root.tag == 'xml':
        for child in root:
            msg[child.tag] = child.text
    return msg

def packet_msg(msg, content):
    msg_template = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>';
    reply_msg = msg_template % (msg['FromUserName'], 
            msg['ToUserName'], msg['CreateTime'], 
            msg['MsgType'], content)
    return reply_msg
