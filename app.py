import os
from flask import Flask, request, jsonify
import yt_dlp
import instaloader

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_video_data():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        if 'instagram.com' in url:
            return extract_using_instaloader(url)
        else:
            return extract_using_ytdlp(url)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_using_ytdlp(url):
    ydl_opts = {'skip_download': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({
            'title': info.get('title'),
            'duration': info.get('duration'),
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'upload_date': info.get('upload_date'),
            'author': info.get('uploader'),
            'comments': info.get('comment_count'),
            'shares': info.get('repost_count')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_using_instaloader(url):
    try:
        L = instaloader.Instaloader()
        shortcode = url.split('/')[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        likes = post.likes
        comments = post.comments
        views = post.video_view_count if post.is_video else None

        return jsonify({
            'likes': likes,
            'views': views,
            'comments': comments
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))