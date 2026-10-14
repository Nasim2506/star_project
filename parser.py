import requests
import time 
import pandas as pd 
from dotenv import load_dotenv
import os 

load_dotenv()

TOKEN = os.getenv('VK_SERVICE_TOKEN')
API_VERSION = os.getenv('VK_API_VERSION')
DOMAIN=os.getenv('VK_TARGET_DOMAIN')
# Правильный URL для метода wall.get
API_URL = 'https://api.vk.com/method/wall.get'

all_posts = []
TOTAL_NEEDED = 300
CHUNK_SIZE = 100

for offset in range(0, TOTAL_NEEDED, CHUNK_SIZE):
    params = {
        'domain': DOMAIN,
        'count': CHUNK_SIZE,
        'offset': offset,
        'access_token': TOKEN,
        'v': API_VERSION
    }
    
    try:
        response = requests.get(API_URL, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"Error at offset {offset}: {data['error']['error_msg']}")
            break
            
        items = data['response']['items']
        if not items:
            break
            
        for post in items:
            if post.get('is_pinned') == 1:
                continue
                
            attachments = post.get('attachments', [])
            
            has_photo = 0
            has_video = 0
            
            for att in attachments:
                att_type = att.get('type')
                if att_type == 'photo':
                    has_photo = 1
                elif att_type in ['video', 'short_video']:
                    has_video = 1
            
            post_text = post.get('text', '').strip()
            has_text = 1 if post_text else 0
            
            all_posts.append({
                'id': post.get('id'),
                'date': post.get('date'),
                'text': post_text,
                'has_text': has_text,
                'has_photo': has_photo,
                'has_video': has_video,
                'likes': post.get('likes', {}).get('count', 0),
                'comments': post.get('comments', {}).get('count', 0),
                'reposts': post.get('reposts', {}).get('count', 0),
                'views': post.get('views', {}).get('count', 0)
            })
            
        print(f"Fetched {offset + len(items)} posts...")
        time.sleep(0.4)
        
    except Exception as e:
        print(f"Fail: {e}")
        break

df = pd.DataFrame(all_posts)
df.to_csv('vk_zhukov_extended.csv', index=False, encoding='utf-8')
print(f"Done. Rows: {len(df)}")