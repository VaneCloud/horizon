# -*-coding:utf-8-*-

# hasApprovalFeature=True: open the approval feature
# hasApprovalFeature=False: close the approval feature
hasApprovalFeature = False

# database
hostname = ''
username = "keystone"
password = ''

# endpoint
compute_endpoint = 'http://172.29.236.100:8774' #nova
identity_endpoint = 'http://172.29.236.100:35357' #keystone

# In order to use the admin user to create a virtual machine
# adminUsername = '4EFFFE084DB1B3AA45C92C79BDA6C66E'
adminUsername = ''
adminPassword = ''

# default roleId is _member_
deafult_roleId = ''

# email information
MAIL_HOST = ''
MAIL_USER = ''
MAIL_PASS = ''
MAIL_POSTFIX = ''
