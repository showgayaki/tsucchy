from googleapiclient.discovery import build


class YouTube:
    def __init__(self, api_version, api_key):
        self.api_version = api_version
        self.api_key = api_key

    def fetch_video_ids(self, channel_id):
        # チャンネルに登録されている動画のidをすべて取得
        next_page_token = None
        npt = None
        video_ids = []
        yt = build('youtube', self.api_version, developerKey=self.api_key)
        while True:
            if next_page_token is not None:
                npt = next_page_token
            try:
                channel_response = yt.search().list(
                    part='id'
                    , channelId=channel_id
                    , pageToken=npt
                    , maxResults=50
                    , order='date'
                ).execute()

                for item in channel_response.get('items', []):
                    if item['id']['kind'] == 'youtube#video':
                        video_ids.append(item['id']['videoId'])
            except Exception as e:
                return 'error: {}'.format(e)
            try:
                next_page_token = channel_response['nextPageToken']
            except:
                break
        return video_ids

    def fetch_videos(self, ids):
        # 一度に渡せるidは50件まで。カンマ区切りで指定する。
        max_results = 50
        split_ids = chunks(ids, max_results)
        ids_csv_list = [','.join(i) for i in split_ids]

        videos = []
        yt = build('youtube', self.api_version, developerKey=self.api_key)
        try:
            for _id in ids_csv_list:
                video_response = yt.videos().list(
                    part='snippet,statistics'
                    , id=_id
                ).execute()
                videos.extend(video_response.get('items'))
        except Exception as e:
            return 'error: {}'.format(e)

        video_dict = {}
        for video in videos:
            video_dict[video['id']] = {}
            video_dict[video['id']]['title'] = video['snippet']['title']
            video_dict[video['id']]['view_count'] = video['statistics']['viewCount']
            video_dict[video['id']]['comment_count'] = video['statistics']['commentCount']

        return video_dict


def chunks(_list, n):
    for i in range(0, len(_list), n):
        yield _list[i:i + n]
