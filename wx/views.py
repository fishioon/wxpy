# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from wx.models import Poll
from wx.models import Choice
from django.utils import timezone
import xml.etree.ElementTree as ET

import hashlib
import random
import requests

# Create your views here.

TOKEN = "fishioon"


class WxMsg:

    def __init__(self):
        self.from_uid = ''
        self.to_uid = ''
        self.content = ''
        self.type = ''
        self.create_time = ''

    def parse_msg(self, text):
        root = ET.fromstring(text)
        if root.tag == 'xml':
            for child in root:
                if child.tag == 'FromUserName':
                    self.from_uid = child.text
                elif child.tag == 'ToUserName':
                    self.to_uid = child.text
                elif child.tag == 'Content':
                    self.content = child.text
                elif child.tag == 'MsgType':
                    self.msg_type = child.text
                elif child.tag == 'CreateTime':
                    self.create_time = child.text
        return True


@csrf_exempt
def wxapp(request):
    if request.method == 'GET':
        str = "success" if check_signature(request) else "failed"
        return HttpResponse(str)
    elif request.method == 'POST':
        return HttpResponse(reply_msg(request))
    else:
        return HttpResponse('Not support http method')


def choice(request):
    if request.method == 'GET':
        context = {'choices': Choice.objects.all()}
        return render(request, 'wx/choices.html', context)


def check_signature(request):
    global TOKEN
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    echostr = request.GET.get("echostr", None)

    token = TOKEN
    tmplist = [token, timestamp, nonce]
    tmplist.sort()
    tmpstr = "%s%s%s" % tuple(tmplist)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    return tmpstr == signature


def get_help_msg():
    msg = (
        "欢迎来到鱼塘，目前这片鱼塘已经被承包啦!\n"
        "使用说明：输入'xh'返回随机返回一个笑话\n"
    )

    #for i in range(0, len(Poll.objects.all())):
    # msg = msg + str(i+1) + ". " + Poll.objects.all()[i].name.encode('utf8')
    # + "\n"
    return msg


def random_poll(msg):
    ranid = random.randint(0, len(Poll.objects.all()) - 1)
    p = Poll.objects.all()[ranid]
    content = p.name.encode('utf8')
    p.votes += 1
    p.save()
    choice = Choice(poll=p, user_id=msg.from_uid, date=timezone.now())
    choice.save()
    return content

# 获取知乎笑话精华中随机一个回答


def random_joke(msg):
    page = random.randint(1, 20)
    num = random.randint(0, 19)
    url = "www.zhihu.com/topic/19563616/top-answers?page=%d" % (page)
    r = requests.get(url, verify=False)
    offset = 0
    for inx in range(0, num):
        offset = r.text.find("data-entry-url=", offset)
        offset += len("data-entry-url=")
    end_off = r.text.find(offset + 1, "\"")
    answer_url = "www.zhihu.com" + r.text[offset + 1, end_off]
    return answer_url


def mark(msg):
    index = msg.content.find('#', 1)
    if index == -1:
        return "您的mark好像有点问题，正确格式为#xxx#具体内容"
    mark_type = msg.content[1:index]
    mark_detail = msg.content[index + 1:]
    mark = Mark(user_id=msg.from_uid,
                date=timezone.now(), type=mark_type, detail=mark_detail)
    mark.save()
    return mark_type + "success"


def reply_msg(request):
    msg = WxMsg()
    msg.parse_msg(request.body)

    if len(msg.content) == 2:
        tx = msg.content.low()
        if tx == 'sj':
            data = random_poll(msg)
        elif tx == 'xh':
            data = random_joke(msg)
    elif msg.content[0] == '#':
        data = mark(msg)
    else:
        data = get_help_msg()
    return packet_msg(msg, data)


def packet_msg(msg, content):
    msg_template = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>'
    reply_msg = msg_template % (
        msg.from_uid, msg.to_uid, msg.create_time, msg.type, content)
    return reply_msg
