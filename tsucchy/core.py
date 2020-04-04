import json
import os
from pathlib import Path
import dotenv
import article
import line_notify
import logger


def load_dotenv(dotenv_path):
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
    return bot.send_message(payload, image)


def main():
    current_path = os.path.abspath(os.path.dirname(__file__))
    dotenv_path = os.path.join(Path(current_path).resolve().parents[0], '.env')

    config = load_dotenv(dotenv_path)
    json_path = os.path.join(current_path, config['JSON_PATH'])

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
        last_dict = load_json(json_path)

        if last_dict == articles_dict:
            log.logging('Not Updated.')
        else:
            if 'error' in last_dict:
                message = ('\nローカルのjsonファイルに問題があります。\n'
                           'ログを確認してください。')
                log.logging(last_dict['error'])
            else:
                log.logging('Updated.')
                message = ('\n記事が更新されたかもです。\n'
                           '内容を確認してください。\n\n'
                           '{}').format(config['TARGET_URL'])

            result = post_line(config['API_URL'], config['ACCESS_TOKEN'], message)
            if result == 200:
                log.logging('Post to LINE Succeeded.')
            else:
                log.logging(result)

            with open(json_path, 'w') as f:
                json.dump(articles_dict, f, indent=4, ensure_ascii=False)
    log.logging('Finish.')


if __name__ == '__main__':
    main()
