#!/usr/bin/env python
#coding:gbk
from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
import base64
import json
import re
import urllib2
import ssl


class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):
        #ע��payload������
        callbacks.registerIntruderPayloadGeneratorFactory(self)
        #���������ʾ������
        callbacks.setExtensionName("xp_CAPTCHA")
        print 'xp_CAPTCHA  ������:Ϲ����֤��\nblog��http://www.nmd5.com/\n�Ŷӹ�����https://www.lonersec.com/ \nThe loner��ȫ�Ŷ� by:�����[��\n\n�÷���\n��headͷ�����http://www.ttshitu.com���˺��������֤���url������֤�����ͣ���","����\n��֤�����ͣ�������=1����Ӣ��=2������Ӣ�Ļ��=3 \n\nxiapao:test,123456,http://www.baidu.com/get-validate-code,3\n\n�磺\n\nPOST /login HTTP/1.1\nHost: www.baidu.com\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\nAccept: text/plain, */*; q=0.01\nAccept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\nContent-Type: application/x-www-form-urlencoded; charset=UTF-8\nX-Requested-With: XMLHttpRequest\nxiapao:test,123456,http://www.baidu.com/get-validate-code,3\nContent-Length: 84\nConnection: close\nCookie: JSESSIONID=24D59677C5EDF0ED7AFAB8566DC366F0\n\nusername=admin&password=admin&vcode=8888\n\n'

    def getGeneratorName(self):
        return "xp_CAPTCHA"

    def createNewInstance(self, attack):
        return xp_CAPTCHA(attack)

class xp_CAPTCHA(IIntruderPayloadGenerator):
    def __init__(self, attack):
        tem = "".join(chr(abs(x)) for x in attack.getRequestTemplate()) #request����
        cookie = re.findall("Cookie: (.+?)\r\n", tem)[0] #��ȡcookie
        xp_CAPTCHA = re.findall("xiapao:(.+?)\r\n", tem)[0]
        ssl._create_default_https_context = ssl._create_unverified_context #����֤�飬��ֹ֤�鱨��
        print xp_CAPTCHA+'\n'
        print 'cookie:' + cookie+'\n'
        self.xp_CAPTCHA = xp_CAPTCHA
        self.cookie = cookie
        self.max = 1 #payload���ʹ�ô���
        self.num = 0 #���payload��ʹ�ô���
        self.attack = attack

    def hasMorePayloads(self):
        #���payloadʹ�õ���������reset����0
        if self.num == self.max:
            return False  # ���ﵽ��������ʱ��͵���reset
        else:
            return True

    def getNextPayload(self, payload):  # ��������뿴���Ľ���
        xp_CAPTCHA_list = self.xp_CAPTCHA.split(',')
        xp_CAPTCHA_user = xp_CAPTCHA_list[0] #��֤��ƽ̨�˺�
        xp_CAPTCHA_pass = xp_CAPTCHA_list[1]    #��֤��ƽ̨����
        xp_CAPTCHA_url = xp_CAPTCHA_list[2] #��֤��url
        if len(xp_CAPTCHA_list) == 4:
            xp_CAPTCHA_type = xp_CAPTCHA_list[3] #��֤������

        #print xp_CAPTCHA_user,xp_CAPTCHA_pass,xp_CAPTCHA_url
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36","Cookie":self.cookie}
        request = urllib2.Request(xp_CAPTCHA_url,headers=headers)
        CAPTCHA = urllib2.urlopen(request) #��ȡͼƬ
        CAPTCHA_base64 = base64.b64encode(CAPTCHA.read()) #��ͼƬbase64����
        if len(xp_CAPTCHA_list) == 4:
            data = '{"username":"%s","password":"%s","image":"%s","typeid":"%s"}'%(xp_CAPTCHA_user,xp_CAPTCHA_pass,CAPTCHA_base64,xp_CAPTCHA_type)
        elif len(xp_CAPTCHA_list) == 3:
            data = '{"username":"%s","password":"%s","image":"%s"}'%(xp_CAPTCHA_user,xp_CAPTCHA_pass,CAPTCHA_base64)
        #print data

        request = urllib2.Request('http://api.ttshitu.com/base64', data,{'Content-Type': 'application/json'})
        response = urllib2.urlopen(request).read()
        print(response)
        result = json.loads(response)
        if result['success']:
            code = result["data"]["result"]
        else:
            code = '0000'
        print code

        return code

    def reset(self):
        self.num = 0  # ����
        return