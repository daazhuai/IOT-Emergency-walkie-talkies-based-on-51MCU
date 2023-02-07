from flask import Flask, request, jsonify, make_response
import api
from WXBizMsgCrypt import WXBizMsgCrypt, ET
import redis


app = Flask(__name__)
token = api.get_token()
my_crypt = WXBizMsgCrypt(api.receive_token, api.AESKey, api.corpid)
r = redis.Redis(host='redis', port=6379, db=0)
p = r.pubsub()


@app.route('/test', methods=["POST"])
def test():
    # 服务器接收消息测试
    if request.method == 'POST':
        json_data = request.get_json()
        print(json_data)
        response = make_response(jsonify({'message': 'OK'}, 200))
        return response


@app.route('/', methods=["GET"])
def check():
    """
    企业微信验证SSL接口
    """

    if request.method == 'GET':
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        _, content = my_crypt.VerifyURL(
            msg_signature, timestamp, nonce, echostr)
        response = make_response(content)
        return response


@app.route('/', methods=["POST"])
def receive():
    """
    企业微信用户发送消息的处理接口
    """
    
    if request.method == 'POST':
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        _, xml_content = my_crypt.DecryptMsg(
            request.get_data(), msg_signature, timestamp, nonce)
        content = ET.fromstring(xml_content).find("Content") # 解码出消息内容
        user = ET.fromstring(xml_content).find("FromUserName") # 解码出用户名
        response = make_response(jsonify({'message': 'OK'}, 200))
        r.publish('w2d-channel', user.text + ": " + content.text) # 向 wechat to desk 频道广播消息
        return response


def message_handler(message):
    """
    订阅消息的处理函数
    @message: String //从websocket服务器端publish来的消息对象
    """
    
    api.send_message_all(message['data'].decode('utf-8'), token)


if __name__ == "__main__":
    app.config['SERVER_NAME'] = 'mylifemeaning.cn:8888'
    p.subscribe(**{'d2w-channel': message_handler}) # 订阅 desk to wechat 频道至 message_handler 函数
    p.run_in_thread(sleep_time=0.001) # 新开一个进程来保证订阅消息被处理
    app.run('0.0.0.0', debug=True, port=8888, ssl_context=(
        "/ssl/2_mylifemeaning.cn.crt", "/ssl/3_mylifemeaning.cn.key")) # 证书通过镜像的方式放置在/ssl目录下
