import requests
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def addTag(html):
    result = html.replace('href="/', f'href="{request.base_url.rsplit("/", 1)[0]}/')
    return result


@app.route('/<path:url>', defaults={'bot': None})
@app.route('/<bot>/<path:url>')
def proxy(bot, url):
    if bot == 'g':
        headers = {'User-Agent': 'Googlebot'}
    else:
        headers = None
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return addTag(r.text)
    except requests.exceptions.HTTPError as e:
        return e.response.text


if __name__ == '__main__':
    app.run()
