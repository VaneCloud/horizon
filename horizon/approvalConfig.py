# -*-coding:utf-8-*-

# hasApprovalFeature=True: open the approval feature
# hasApprovalFeature=False: close the approval feature
hasApprovalFeature=False

# database 
hostname="172.29.236.100"
username = "root"
password="6400c0708f945d3dbe9c90c4dec5938ce494b2"

# endpoint
compute_endpoint = 'http://172.29.236.100:8774' #nova
identity_endpoint = 'http://172.29.236.100:35357' #keystone

# In order to use the admin user to create a virtual machine
# adminUsername = '4EFFFE084DB1B3AA45C92C79BDA6C66E'
adminUsername = '9EFFFE084DB1B3AA45C92C79BDA6C66EK'
adminPassword = 'D76FE65DA62B58ED9CDD84F8FED1C941E9D1B297'

# default roleId is _member_
deafult_roleId = '9fe2ff9ee4384b1894a90878d3e92bab'

# email information
MAIL_HOST = "smtp.163.com"
MAIL_USER = "openstackTestmail"  
MAIL_PASS = "openstack123"  
MAIL_POSTFIX = "163.com"
