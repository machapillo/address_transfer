import json
import requests
from datetime import datetime
import os

def handler(event, context):
    # CORS対応
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    # OPTIONSリクエスト（CORS preflight）
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # POSTリクエストのみ処理
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # リクエストボディを解析
        body = json.loads(event['body'])
        address = body.get('address', '').strip()
        
        if not address:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': '住所を入力してください'})
            }
        
        # 住所から緯度経度を取得
        lat, lon, status = get_coordinates(address)
        
        # 結果を返す
        result = {
            'address': address,
            'latitude': lat,
            'longitude': lon,
            'status': status,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def get_coordinates(address):
    try:
        # OpenStreetMap Nominatim APIを使用
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'GeocodingApp/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon, "成功"
        else:
            return None, None, "住所が見つかりません"
    except Exception as e:
        return None, None, f"エラー: {str(e)}"
