# coding=utf-8
import sys, os, base64, datetime, hashlib, hmac
import requests

method = 'GET'
service = 'ec2'
host = 'ec2.amazonaws.com'
region = 'us-east-1'
endpoint = 'https://ec2.amazonaws.com'
request_parameters = 'Action=DescribeRegions&Version=2013-10-15'

# 署名キー取得関数


def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning


def lambda_handler(event, context):
# 環境変数からアクセスキーとシークレットアクセスキーを取得
    access_key = os.environ.get('USER_AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('USER_AWS_SECRET_ACCESS_KEY')
    if access_key is None or secret_key is None:
        print('No access key is available.')
        sys.exit()

# タイムスタンプ生成
    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')

# ************* タスク1: 正規リクエストの作成 *************
# http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

# Step 1 最初に HTTP リクエストメソッド (GET、PUT、POST など) を指定。
# methodで指定済み

# Step 2: 正規 URI パラメータを追加。
    canonical_uri = '/'

# Step 3: 正規クエリ文字列を追加し、その後に改行文字を置きます。
# リクエストにクエリ文字列が含まれていない場合は、空の文字列 (主に空白行) を使用します。このリクエスト例には次のクエリ文字列が含まれます。
    canonical_querystring = request_parameters

# Step 4: 正規ヘッダーを追加し、その後に改行文字を置きます。
    canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n'

# Step 5: 署名付きヘッダーを追加
    signed_headers = 'host;x-amz-date'

# Step 6: HTTP または HTTPS リクエストの本文のペイロードからハッシュ値を作成します。
    payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()

# Step 7: 最終的な正規リクエストを作成するには、各手順のすべてのコンポーネントを単一の文字列として結合します。
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

# ************* タスク 2: 署名バージョン 4 の署名文字列を作成する*************
# アルゴリズムを指定
# SHA-1 or SHA-256 (recommended)
    algorithm = 'AWS4-HMAC-SHA256'
# 要求日付の値と認証情報スコープの値を追加
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
# タスク1で作成した正規リクエストのハッシュを追加
    string_to_sign = algorithm + '\n' + amzdate + '\n' + credential_scope + '\n' + hashlib.sha256(
        canonical_request.encode('utf-8')).hexdigest()

# ************* タスク 3: AWS署名バージョン 4 の署名を計算する *************
# 署名キーを取得
    signing_key = getSignatureKey(secret_key, datestamp, region, service)

# 署名を計算
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

# ************* タスク 4: リクエストに署名を追加する *************
# Authorization ヘッダーに署名情報を追加する
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

    headers = {'x-amz-date': amzdate, 'Authorization': authorization_header}

# ************* リクエストを送信する *************
    request_url = endpoint + '?' + canonical_querystring

    print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
    print('Request URL = ' + request_url)
    r = requests.get(request_url, headers=headers)

    print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
    print('Response code: %d\n' % r.status_code)
    print(r.text)
