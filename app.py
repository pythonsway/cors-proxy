from urllib.parse import parse_qs, urlencode, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def add_tag(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    urls = {'href': ['a', 'link'],
            'src': ['img', 'script']}
    for attr, tagList in urls.items():
        for tags in tagList:
            for tag in soup.findAll(tags):
                if tag.has_attr(attr):
                    if not tag[attr].startswith('http'):
                        # scheme://netloc/path;parameters?query#fragment
                        url_parsed = urlparse(url)
                        query_parsed = parse_qs(url_parsed.query)
                        query_parsed['url'][0] = urljoin(query_parsed['url'][0], tag[attr])
                        new_query = urlencode(query_parsed, doseq=True)
                        new_url = url_parsed._replace(query=new_query).geturl()
                        tag[attr] = new_url
    result = str(soup)
    return result


@app.route('/ping')
def hello_world():
    return 'pong'


@app.route('/proxy')
def proxy():
    if url_query := request.args.get('url'):
        if request.args.get('bot') == 'g':
            headers = {'User-Agent': 'Googlebot'}
        else:
            headers = {'User-Agent': f'{request.user_agent}'}
        try:
            r = requests.get(url_query, headers=headers)
            r.raise_for_status()
            # exclude "hop-by-hop headers" +  x-frame-options
            excluded_headers = ['content-encoding', 'content-length',
                                'transfer-encoding', 'connection', 'x-frame-options']
            headers = [(name, value) for (name, value) in r.raw.headers.items()
                       if name.lower() not in excluded_headers]
            # headers['Content-Security-Policy'] = "default-src 'self'"
            if 'text/html' in r.headers["content-type"]:
                content = add_tag(r.text, request.url)
            else:
                content = r.content
            response = Response(content, r.status_code, headers)
            return response
        except requests.exceptions.HTTPError as e:
            return e.response.text
    else:
        return 'no url'


if __name__ == '__main__':
    app.run()
