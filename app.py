pip install matplotlib
# ======python的函數庫==========
# ... (你现有的代码)

# 导入必要的库
from io import BytesIO
import matplotlib.pyplot as plt

# ... (你现有的代码)

# 根据用户输入生成柱状图的函数
def generate_chart(input_data):
    # 用你自己的逻辑替换这里的 input_data 处理逻辑以及生成图表数据
    data = {'类别A': 10, '类别B': 20, '类别C': 15}

    # 创建一个简单的柱状图
    plt.bar(data.keys(), data.values())
    plt.xlabel('类别')
    plt.ylabel('数值')
    plt.title('样本柱状图')

    # 将图表保存到 BytesIO 对象
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    # 为下一个图表清除绘图区域
    plt.clf()

    return image_stream

# ... (你现有的代码)

# 修改 handle_message 函数以包含图表生成
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    try:
        # 生成 GPT 回复
        GPT_answer = GPT_response(msg)

        # 根据 GPT 回复生成图表
        chart_stream = generate_chart(GPT_answer)

        # 发送 GPT 回复文本和图表
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text=GPT_answer),
            ImageSendMessage(original_content_url='https://your-chart-url-here', preview_image_url='https://your-chart-url-here')
        ])
    except Exception as e:
        print(traceback.format_exc())
        line_bot_api.reply_message(event.reply_token, TextSendMessage('错误: {}'.format(str(e))))

# ... (你现有的代码)

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
import traceback
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')


def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    try:
        GPT_answer = GPT_response(msg)
        print(GPT_answer)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
    except:
        print(traceback.format_exc())
        line_bot_api.reply_message(event.reply_token, TextSendMessage('你所使用的OPENAI API key額度可能已經超過，請於後台Log內確認錯誤訊息'))
        

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
