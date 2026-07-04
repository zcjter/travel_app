"""测试上传接口"""
import sys
sys.path.insert(0, '.')
from urllib.request import urlopen, Request
import json
import os

BASE = 'http://127.0.0.1:8001'

# 1. 测试根路由
resp = urlopen(BASE + '/')
print('GET /:', resp.status, resp.read().decode()[:100])

# 2. 测试上传
boundary = '----TestBoundary'
body_parts = []
body_parts.append('--' + boundary)
body_parts.append('Content-Disposition: form-data; name="file"; filename="test.jpg"')
body_parts.append('Content-Type: image/jpeg')
body_parts.append('')
body_parts.append('')  # 留空给二进制数据

header = '\r\n'.join(body_parts[:4]) + '\r\n'
footer = '\r\n--' + boundary + '--\r\n'

with open('test_upload.jpg', 'rb') as f:
    img_data = f.read()

body = header.encode() + img_data + footer.encode()

req = Request(BASE + '/upload', data=body)
req.add_header('Content-Type', 'multipart/form-data; boundary=' + boundary)

try:
    resp = urlopen(req)
    print('\nUpload status:', resp.status)
    data = json.loads(resp.read())
    print('Result:', json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print('\nUpload Error:', e)
    if hasattr(e, 'read'):
        print('Body:', e.read().decode()[:500])

# 清理
os.remove('test_upload.jpg')
