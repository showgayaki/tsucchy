import json
import os
from pathlib import Path
import dotenv
from article import LatestArticles
from line_notify import LineNotify
from youtube import YouTube
from logger import Logger


def load_dotenv(dotenv_path):
    dotenv.load_dotenv(dotenv_path)
    config_dict = {
        'TARGET_URL': os.environ.get('TARGET_URL')
        , 'TARGET_ID': os.environ.get('TARGET_ID')
        , 'API_URL': os.environ.get('API_URL')
        , 'ACCESS_TOKEN': os.environ.get('ACCESS_TOKEN')
        , 'YOUTUBE_API_KEY': os.environ.get('YOUTUBE_API_KEY')
        , 'YOUTUBE_API_VERSION': os.environ.get('YOUTUBE_API_VERSION')
        , 'CHANNEL_ID': os.environ.get('CHANNEL_ID')
        , 'CHANNEL_URL': os.environ.get('CHANNEL_URL')
        , 'JSON_FILE': os.environ.get('JSON_FILE')
    }
    return config_dict


def load_json(json_path):
    last_dict = {}
    try:
        last_dict = json.load(open(json_path))
    except Exception as e:
        last_dict['error'] = str(e)

    return last_dict


def save_json(json_path, data):
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def message(**kwargs):
    article_msg = ''
    video_msg = ''
    if 'error' in kwargs['articles_dict']:
        kwargs['log'].logging(kwargs['articles_dict']['error'])
        article_msg = ('\n最近の投稿を取得できませんでした。\n'
                       '確認してください。\n')

    if 'error' in kwargs['last_dict']['articles']:
        kwargs['log'].logging(kwargs['last_dict']['articles']['error'])
        article_msg += ('\nローカルのjsonファイルに問題があります。\n'
                        'ログを確認してください。\n')

    if kwargs['last_dict']['articles'] == kwargs['articles_dict']:
        kwargs['log'].logging('Not Updated articles.')
    elif article_msg == '':
        kwargs['log'].logging('Updated articles.')
        article_msg += ('\n記事が更新されたかもです。\n'
                        '内容を確認してください。\n\n'
                        '{}\n').format(kwargs['config']['TARGET_URL'])

    if 'error' in kwargs['video_ids']:
        kwargs['log'].logging(kwargs['video_ids'])
        video_msg += '\nチャンネル情報の取得に失敗しました。'
    elif 'error' in kwargs['videos']:
        kwargs['log'].logging(kwargs['videos'])
        video_msg += '\n動画情報の取得に失敗しました。'

    if kwargs['last_dict']['videos'].keys() == kwargs['videos'].keys():
        kwargs['log'].logging('Not Updated videos.')
    elif video_msg == '':
        kwargs['log'].logging('Updated videos.')
        video_msg += ('\n動画が更新されたかもです。\n'
                      '内容を確認してください。\n\n'
                      '{}').format(kwargs['config']['CHANNEL_URL'])

    return article_msg + video_msg


def post_line(api_url, access_token, msg):
    bot = LineNotify(api_url, access_token)
    payload = {
        'message': msg
        , 'stickerPackageId': None
        , 'stickerId': None
    }
    image = None
    return bot.send_message(payload, image)


def main():
    log = Logger(os.path.dirname(__file__), 10)
    log.logging('Start.')

    current_path = os.path.abspath(os.path.dirname(__file__))
    dotenv_path = os.path.join(Path(current_path).resolve().parents[0], '.env')
    config = load_dotenv(dotenv_path)
    json_dir = os.path.join(current_path, 'json')
    json_path = os.path.join(json_dir, config['JSON_FILE'])

    # YouTubeの指定チャンネルの動画すべて取得
    yt = YouTube(config['YOUTUBE_API_VERSION'], config['YOUTUBE_API_KEY'])
    video_ids = yt.fetch_video_ids(config['CHANNEL_ID'])
    if 'error' in video_ids:
        log.logging('Channel {}'.format(video_ids))
        videos = {}
    else:
        videos = yt.fetch_videos(video_ids)
    # ブログから最近の投稿取得
    articles = LatestArticles(config['TARGET_URL'], config['TARGET_ID'])
    articles_dict = articles.fetch_latest_articles()
    latest = {'articles': articles_dict, 'videos': videos}

    # 取得した情報をjsonで保存。
    if not os.path.isdir(json_dir):
        os.makedirs(json_dir)
        log.logging('Created Directory => [{}]'.format(json_dir))
        save_json(json_path, latest)
        last_dict = load_json(json_path)
    else:
        last_dict = load_json(json_path)
        save_json(json_path, latest)
    log.logging('Saved json => [{}]'.format(json_path))

    msg = message(**vars())

    if msg:
        post_result = post_line(config['API_URL'], config['ACCESS_TOKEN'], msg)
        if post_result == 200:
            log.logging('Post to LINE Succeeded.')
        else:
            log.logging(post_result)

    log.logging('Finish.')


if __name__ == '__main__':
    main()
