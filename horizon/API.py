# -*-coding:utf-8-*-
import json
import urllib2

import smtplib, mimetypes
from email.Header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import MySQLdb

from horizon import approvalConfig

reload(sys)
sys.setdefaultencoding('utf-8')

# compute_endpoint = 'http://192.168.104.220:8774'
# identity_endpoint = 'http://192.168.104.220:35357'
# 用于创建虚拟机的管理员账号和密码,由该用户代理创建虚拟机
# username = '4EFFFE084DB1B3AA45C92C79BDA6C66E'
# password = 'D76FE65DA62B58ED9CDD84F8FED1C941E9D1B297'

# 新建用户的角色ID，默认为_member_
# deafult_roleId = '9fe2ff9ee4384b1894a90878d3e92bab'

def send_mail(subject, content, email_address): 

    MAIL_HOST = approvalConfig.MAIL_HOST
    MAIL_USER = approvalConfig.MAIL_USER
    MAIL_PASS = approvalConfig.MAIL_PASS
    MAIL_POSTFIX = approvalConfig.MAIL_POSTFIX
    MAIL_FROM = MAIL_USER + "<" + MAIL_USER + "@" + MAIL_POSTFIX + ">"

    try:
        MAIL_LIST = [email_address] 
        if isinstance(content, unicode):
            content = str(content)
            
        message = MIMEText(content, 'plain', 'utf-8')
        if isinstance(subject, unicode):
            subject = unicode(subject)
        message["Subject"] = Header(subject, 'utf-8')
        message["From"] = MAIL_FROM 
        message["To"] = ";".join(MAIL_LIST)
        message["Accept-Language"] = "zh-CN"
        message["Accept-Charset"] = "ISO-8859-1,utf-8"
        smtp = smtplib.SMTP() 
        smtp.connect(MAIL_HOST) 
        smtp.login(MAIL_USER, MAIL_PASS) 
        smtp.sendmail(MAIL_FROM, MAIL_LIST, message.as_string()) 
        smtp.close() 
        return True
    except Exception, errmsg: 
        print "Send mail failed to: %s" % errmsg
        return False

def isCurrentUserAdmin(request):
    try:
        conn = MySQLdb.connect(approvalConfig.hostname, approvalConfig.username, approvalConfig.password, "keystone",charset='utf8')
        cur=conn.cursor()
        sql = 'SELECT user_id FROM token WHERE id = %s'
        current_user_token = request.session['unscoped_token']
        args = [current_user_token]
        cur.execute(sql,args)
        results = cur.fetchall()
        current_userId = ""
        for r in results:
            current_userId = r[0]

        sql = 'SELECT name FROM user WHERE id = %s'
        args = [current_userId]
        cur.execute(sql,args)
        results = cur.fetchall()
        current_userName = ""
        for r in results:
            current_userName = r[0]

        isAdmin = False
        if current_userName=="admin":
            isAdmin = True
        cur.close()
        conn.close()
        return isAdmin
    except Exception, errmsg: 
         print "Failed check isAdmin: %s" % errmsg
         return False


# 执行GET的request，将response的JSON转换成字典返回
def get(url, token):
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'application/json')
    request.add_header('X-Auth-Token', token)
    response = urllib2.urlopen(request)
    return json.loads(response.read())

# 执行POST的request，将response的JSON转换成字典返回
def post(url, token, data):
    data = json.dumps(data)
    request = urllib2.Request(url, data)
    request.add_header('Content-Type', 'application/json')
    if token is not None:
        request.add_header('X-Auth-Token', token)
    response = urllib2.urlopen(request)
    return json.loads(response.read())

# 执行PUT的request，将response的JSON转换成字典返回
def put(url, token):
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'application/json')
    request.add_header('X-Auth-Token', token)
    request.get_method = lambda:'PUT'
    response = urllib2.urlopen(request)
    return json.loads(response.read())

# 执行DELETE的request，将response的JSON转换成字典返回
def delete(url, token):
    request = urllib2.Request(url)
    request.add_header('X-Auth-Token', token)
    request.get_method = lambda:'DELETE'
    urllib2.urlopen(request)

# 获得管理员令牌API
def get_token(token):
    url = approvalConfig.identity_endpoint + '/v2.0/tokens'
    data = {
        'auth': {
            'tenantName': 'admin',
            'token': {
                'id': token
            }
        }
    }
    return post(url, token, data)['access']['token']['id']


# 获得管理员令牌API
def get_token_by_tenant_id(tenant_id):
    url = approvalConfig.identity_endpoint + '/v2.0/tokens'
    data = {
        'auth': {
            'tenantId': tenant_id,
            'passwordCredentials': {
                'username': approvalConfig.adminUsername,
                'password': approvalConfig.adminPassword
            }
        }
    }
    return post(url, None, data)['access']['token']['id']

# 添加一个用户API
def add_user(token, name, password, email):
    url = approvalConfig.identity_endpoint + '/v2.0/users'
    data = {
        'user': {
            'name': name,
            'email': email,
            'enabled': True,
            'OS-KSADM:password': password
        }
    }
    return post(url, get_token(token), data)

# 为用户在tenant中添加角色API
def add_role(token, tenantId, userId):
    url = approvalConfig.identity_endpoint + '/v2.0/tenants/%s/users/%s/roles/OS-KSADM/%s' % (tenantId, userId, approvalConfig.deafult_roleId)
    put(url, get_token(token));

# 删除一个用户
# 未完成
def delete_user(userId, token):
    url = approvalConfig.identity_endpoint + '/v2.0/users/' + userId
    return delete(url, get_token(token))

# 创建一个虚拟机API
def create_server(tenant_id, name, image_id, flavor_id):
    url = approvalConfig.compute_endpoint + '/v2/%s/servers' % tenant_id
    data = {
        'server': {
            'name': name,
            'imageRef': image_id,
            'flavorRef': flavor_id,
        }
    }
    return post(url, get_token_by_tenant_id(tenant_id), data)['server']['id']

# Network HA
def get_token_HA(tenant_id):
    url = approvalConfig.identity_endpoint + '/v2.0/tokens'
    data = {
        'auth': {
            'tenantId': tenant_id,
            'passwordCredentials': {
                'username': 'kevin',
                'password': '123456'
            }
        }
    }
    return post(url, None, data)['access']['token']['id']

#select price from database
def getPrice():
    try:
        conn = MySQLdb.connect(approvalConfig.hostname, approvalConfig.username, approvalConfig.password, "keystone",charset='utf8')
        cur=conn.cursor()
        sql = 'SELECT vcpu,memory,disk,currency FROM price where id=1'
        cur.execute(sql)
        results = cur.fetchall()
        vcpuprice = 0
        memoryprice = 0
        diskprice = 0
        currency = 1
        for r in results:
            vcpuprice = r[0]
            memoryprice = r[1]
            diskprice = r[2]
            currency = r[3]
        cur.close()
        conn.close()
        return vcpuprice,memoryprice,diskprice,currency
    except Exception, errmsg: 
         print "Failed connect database: %s" % errmsg
         return 0,0,0,1

#update price
def updatePrice(vcpuPrice,memoryPrice,diskPrice,currency):
    try:
        conn = MySQLdb.connect(approvalConfig.hostname, approvalConfig.username, approvalConfig.password, "keystone",charset='utf8')
        cur=conn.cursor()
        sql = 'UPDATE price SET vcpu=%s , memory=%s , disk=%s , currency=%s where id=1'
        args = [vcpuPrice,memoryPrice,diskPrice,currency]
        cur.execute(sql,args)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception, errmsg: 
         print "Failed connect database: %s" % errmsg
         return False