import os
import requests
from flask import Flask, request, jsonify
import yt_dlp
import instaloader
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/extract', methods=['POST'])
def extract_video_data():
    urls = request.json.get('urls')
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400

    results = []

    for url in urls:
        try:
            if 'tiktok.com/t/' in url:
                resolved_url = resolve_tiktok_url(url)
            else:
                resolved_url = url

            if 'instagram.com' in resolved_url:
                result = extract_using_instaloader(resolved_url)
            else:
                result = extract_using_ytdlp(resolved_url)
            results.append(result)
        except Exception as e:
            results.append({'url': url, 'error': str(e)})

    return jsonify(results), 200

def resolve_tiktok_url(url):
    try:
        response = requests.get(url, allow_redirects=True)
        return response.url
    except requests.RequestException as e:
        return url

def extract_using_ytdlp(url):
    scraperapi_key = "1c8a4d9d153ef5b9950f3f2324ebac45"
    proxy_url = f"http://scraperapi:{scraperapi_key}@proxy-server.scraperapi.com:8001"
    
    ydl_opts = {
        'skip_download': True,
        'proxy': proxy_url,
        'nocheckcertificate': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        upload_date = info.get('upload_date')
        if upload_date:
            upload_date = datetime.strptime(upload_date, '%Y%m%d').strftime('%Y-%m-%d')
        
        return {
            'url': url,
            'title': info.get('title'),
            'duration': info.get('duration'),
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'upload_date': upload_date,
            'author': info.get('uploader'),
            'comments': info.get('comment_count'),
            'shares': info.get('repost_count')
        }
    except Exception as e:
        return {'url': url, 'error': str(e)}

def extract_using_instaloader(url):
    scraperapi_key = "1c8a4d9d153ef5b9950f3f2324ebac45"
    proxy_url = f"http://scraperapi:{scraperapi_key}@proxy-server.scraperapi.com:8001"

    L = instaloader.Instaloader()
    L.context.proxy = proxy_url
    
    try:
        shortcode = url.split('/')[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        return {
            'url': url,
            'likes': post.likes,
            'views': post.video_view_count if post.is_video else None,
            'comments': post.comments
        }
    except Exception as e:
        return {'url': url, 'error': str(e)}
    
@app.route("/cron_trigger", methods=["POST"])
def cron_trigger():
    # Aquí haces la petición a tu servidor en DigitalOcean
    response = requests.post("https://blitz-app-u3rzf.ondigitalocean.app/api/cron/example_task")
    return "Cron job ejecutado", response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
