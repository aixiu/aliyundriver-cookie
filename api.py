from flask import Flask, request
import requests, qrcode, base64, json

app = Flask(__name__)
# set static folder
app.static_folder = 'static'


@app.route('/')
def index():
    # index.html
    return app.send_static_file('index.html')


@app.route('/index.js')
def index_js():
    # index.js
    return app.send_static_file('index.js')


@app.route('/api')
def api():
    return 'API'


@app.route('/api/newqrcode')
def newqrcode():
    resp = requests.get(
        'https://passport.aliyundrive.com/newlogin/qrcode/generate.do?' +
        'appName=aliyun_drive' + '&fromSite=52' + '&appName=aliyun_drive' +
        '&appEntrance=web' + 
        '&isMobile=false' + 
        '&lang=zh_CN' +
        '&returnUrl=' + 
        '&bizParams=' + 
        '&_bx-v=2.0.31',
        headers={
            'Access-Control-Allow-Origin': '*',
        },
        timeout=3,
    )
    if resp.status_code != 200:
        return 'error'
    codeContent = resp.json()['content']['data']['codeContent']
    ck = resp.json()['content']['data']['ck']
    t = resp.json()['content']['data']['t']
    # url to qrcode
    img = qrcode.make(codeContent)
    # save qrcode
    img.save('qrcode.png')
    # qrcode to base64
    with open('qrcode.png', 'rb') as f:
        base64_data = base64.b64encode(f.read())
        s = base64_data.decode()
    codeContent = 'data:image/png;base64,' + s
    return json.dumps({
        'codeContent': codeContent,
        'ck': ck,
        't': t,
    })


@app.route('/api/statecheck')
def statecheck():

    ck = request.args.get('ck')
    t = request.args.get('t')
    resp = requests.post(
        'https://passport.aliyundrive.com/newlogin/qrcode/query.do?' +
        'appName=aliyun_drive' + 
        '&fromSite=52' + 
        '&_bx-v=2.0.31',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        },
        data={
            't': t,
            'ck': ck,
            'appName': 'aliyun_drive',
            'appEntrance': 'web',
            'isMobile': 'false',
            'lang': 'zh_CN',
            'returnUrl': '',
            'fromSite': '52',
            'bizParams': '',
            'navlanguage': 'zh-CN',
            'navPlatform': 'MacIntel',
        },
        timeout=3,
    )
    if resp.status_code != 200:
        return 'error'
    content = resp.json()['content']
    qrCodeStatus = content['data']['qrCodeStatus']

    content['data']['tip'] = {
        'NEW': '请用阿里云盘 App 扫码',
        'SCANED': '请在手机上确认',
        'EXPIRED': '二维码已过期',
        'CANCELED': '已取消',
        'CONFIRMED': '已确认',
    }[qrCodeStatus]
    if qrCodeStatus == 'CONFIRMED':
        content['data']['bizExt'] = json.loads(
            base64.b64decode(
                content['data']['bizExt']).decode(encoding='Latin-1'))
        print(content['data']['bizExt'])
    return json.dumps(content)


if __name__ == '__main__':
    # debug
    app.run()