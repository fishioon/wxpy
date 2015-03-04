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

# Create your views here.

TOKEN = "fishioon"

@csrf_exempt
def wxapp(request):
    if request.method == 'GET':
        return HttpResponse(check_signature(request))
    elif request.method == 'POST':
        return HttpResponse(reply_msg(request))
    else:
        return HttpResponse('Not support http method') 

def choice(request):
    if request.method == 'GET':
        context = {'choices' : Choice.objects.all()}
        return render(request, 'wx/choices.html', context)

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

def get_help_msg():
    msg = ("欢迎使用爱情上上签，为你的TA求支签!\n"
            "使用说明：输入'sj'返回求签结果\n"
            "目前已有的签如下：\n")

    for i in range(0, len(Poll.objects.all())):
        msg = msg + str(i+1) + ". " + Poll.objects.all()[i].name.encode('utf8') + "\n"
    return msg

def reply_msg(request):
    msg = parse_msg(request.body)
    req_data = msg['Content']
    data = ""
    if msg['MsgType'] == 'text' and req_data.lower() == 'sj':
        ranid = random.randint(0, len(Poll.objects.all())-1)
        p = Poll.objects.all()[ranid]
        data = p.name.encode('utf8')
        p.votes += 1
        p.save()
        choice = Choice(poll=p, user_id=msg['FromUserName'], date=timezone.now())
        choice.save()
    else:
        data = get_help_msg()
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
