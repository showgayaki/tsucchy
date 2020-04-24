import requests
from bs4 import BeautifulSoup


class LatestArticles:
    """
    urlと新着記事箇所のidを指定して、
    記事タイトルとリンクurlをDictionaryにして返す
    articles_dict = {
        'article_1': {
            'title': '記事タイトル',
            'link': 'https://example.com/article_1'
        }
    }
    """
    def __init__(self, target_url, target_id):
        self.target_url = target_url
        self.target_id = target_id

    def fetch_latest_articles(self):
        articles_dict = {}
        try:
            r = requests.get(self.target_url, timeout=(3, 6))
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                latest_articles = soup.select('#{} a'.format(self.target_id))

                for i, elem in enumerate(latest_articles):
                    key = 'article_{}'.format(i + 1)
                    articles_dict[key] = {}
                    articles_dict[key]['title'] = elem.contents[0]
                    articles_dict[key]['link'] = elem.attrs['href']
            else:
                articles_dict['error'] = 'Status Code:{} From:{}'.format(r.status_code, self.target_url)
        except Exception as e:
            articles_dict['error'] = str(e)

        return articles_dict

