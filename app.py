import os
from flask import Flask, request, jsonify
import yt_dlp
import instaloader
from flask_cors import CORS

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
            if 'instagram.com' in url:
                result = extract_using_instaloader(url)
            else:
                result = extract_using_ytdlp(url)
            results.append(result)
        except Exception as e:
            results.append({'url': url, 'error': str(e)})

    return jsonify(results), 200

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
        return {
            'url': url,
            'title': info.get('title'),
            'duration': info.get('duration'),
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'upload_date': info.get('upload_date'),
            'author': info.get('uploader'),
            'comments': info.get('comment_count'),
            'shares': info.get('repost_count')
        }
    except Exception as e:
        return {'url': url, 'error': str(e)}

def extract_using_instaloader(url):
    scraperapi_key = "1c8a4d9d153ef5b9950f3f2324ebac45"
    proxy_url = f"http://scraperapi:{scraperapi_key}@proxy-server.scraperapi.com:8001"

    # Crear una sesión con el proxy en Instaloader
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
