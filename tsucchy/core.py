import json
import os
import pathlib
import dotenv
import article
import line_notify
import logger


def load_dotenv():
    dotenv_path = os.path.join(pathlib.Path(__file__).parents[1], '.env')
    dotenv.load_dotenv(dotenv_path)
    config_dict = {
        'TARGET_URL': os.environ.get('TARGET_URL')
        , 'TARGET_ID': os.environ.get('TARGET_ID')
        , 'API_URL': os.environ.get('API_URL')
        , 'ACCESS_TOKEN': os.environ.get('ACCESS_TOKEN')
        , 'JSON_PATH': os.environ.get('JSON_PATH')
    }
    return config_dict


def load_json(json_path):
    last_dict = {}
    try:
        last_dict = json.load(open(json_path))
    except Exception as e:
        last_dict['error'] = str(e)

    return last_dict


def post_line(api_url, access_token, message):
    bot = line_notify.LineNotify(api_url, access_token)
    payload = {
        'message': message
        , 'stickerPackageId': None
        , 'stickerId': None
    }
    image = None
    bot.send_message(payload, image)


def main():
    config = load_dotenv()
    log = logger.Logger(os.path.dirname(__file__), 10)
    log.logging('Start.')
    articles = article.LatestArticles(config['TARGET_URL'], config['TARGET_ID'])
    articles_dict = articles.fetch_latest_articles()

    if 'error' in articles_dict:
        log.logging(articles_dict['error'])
    else:
        json_dir = os.path.join(os.path.dirname(__file__), 'json')
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
            log.logging('Created Directory => [{}]'.format(json_dir))
        last_dict = load_json(config['JSON_PATH'])

        if last_dict == articles_dict:
            log.logging('Not Update.')
        else:
            if 'error' in last_dict:
                message = ('\nローカルのjsonファイルに問題があります。\n'
                           'ログを確認してください。')
                log.logging(last_dict['error'])
            else:
                message = ('\n記事が更新されたかもです。\n'
                           '内容を確認してください。\n\n'
                           '{}').format(config['TARGET_URL'])

            post_line(config['API_URL'], config['ACCESS_TOKEN'], message)
            with open(config['JSON_PATH'], 'w') as f:
                json.dump(articles_dict, f, indent=4, ensure_ascii=False)
    log.logging('Finish.')


if __name__ == '__main__':
    main()
