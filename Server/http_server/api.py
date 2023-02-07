import requests
import yaml

# 从config.yaml中读取参数
config_file = open("config.yaml", "r", encoding="utf-8")
config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
config_file.close()
corpid = config["corpid"]
corpsecret = config["corpsecret"]
receive_token = config["receive_token"]
AESKey = config["AESKey"]


def get_token():
    # 使用corpid和corpsecret换取token
    res = requests.get(
        "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s" % corpid + "&corpsecret=%s" % corpsecret)
    return res.json()['access_token']


def send_message_all(message, token):
    """
    将此消息发送至全部订阅企业号的用户

    @message: String // 要发送的消息
    @token: String // 微信api认证token
    
    返回发送结果
    """
    request_body = """{
       "touser" : "@all",
       "msgtype" : "text",
       "agentid" : 1000002,
       "text" : {
           "content" : "%s""" % message + """"
    },
    "safe": 0,
    "enable_id_trans": 0,
    "enable_duplicate_check": 0,
    "duplicate_check_interval": 1800
    }"""
    res = requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' % token,
                        data=request_body.encode('utf-8'))
    print(res)
    return res
