# coding=utf-8
import os
import BiliUtil.Util as Util
import BiliUtil.Space as Space
import BiliUtil.Video as Video
from tqdm import tqdm


class Fetcher:
    def __init__(self, obj):
        self.obj = obj
        self.info_list = None
        self.task_list = None
        self.exist_list = None

    def fetch_all(self, cookie=None, name_pattern=Util.Config.SET_AS_CODE, quality=None):
        """
        自动获取用户与频道名下的所有视频信息
        :param cookie: 权限信息
        :param quality: 下载视频质量
        :param name_pattern: 路径命名方式
        :return: 所有视频的av号列表
        """
        av_list = []
        self.info_list = []

        # 确定对象类型
        if isinstance(self.obj, Space.User):
            obj_code = self.obj.uid
        elif isinstance(self.obj, Space.Channel):
            obj_code = self.obj.cid
        else:
            raise Util.ParameterError('该类型对象无法自动加载')

        # 逐级确定储存路径
        if name_pattern == Util.Config.SET_AS_CODE:
            obj_name = obj_code
        elif name_pattern == Util.Config.SET_AS_NAME:
            self.obj.sync()
            obj_name = Util.legalize_name(self.obj.name)
        elif name_pattern == Util.Config.SET_AS_PAGE:
            self.obj.sync()
            obj_name = Util.legalize_name(self.obj.name)
        else:
            obj_name = "unknown"

        album_list = self.obj.get_album_list()
        for album in tqdm(album_list, desc="Fetching..."):
            try:
                album.sync(cookie)
            except Util.RunningError:
                print("404 or 403 on: %s, skipped"%album.aid)
                continue
            album_name = album.album_name(name_pattern)

            video_list = album.get_video_list()
            for video in video_list:
                video.sync(cookie, quality)
                video_name = video.video_name(name_pattern)

                self.info_list.append({
                    'obj': (obj_name, self.obj),
                    'album': (album_name, album),
                    'video': (video_name, video)
                })
                av_list.append(album.aid)
        av_list = list(set(av_list))
        return av_list

    def load_task(self, output, exclude=None, v_filter=None, keyword_filter=None ):
        """
        自动完成下载任务的批量生成
        :param output: 输出路径
        :param exclude: 排除列表
        :param v_filter:
        :return: 下载列表中视频av号
        """
        task_list = []
        self.task_list = []
        base_path = os.path.abspath(output)
        exclude = [str(item) for item in exclude]

        # 逐个过滤并生成任务
        for info in self.info_list:
            # 执行过滤策略
            if info['album'][1].aid in exclude:
                continue
            elif keyword_filter in info['album'][1].name:
                continue
            elif v_filter is not None and v_filter.check_video(info['video'][1]):
                continue

            # 创建新的下载任务
            full_path = os.path.join(base_path, info['obj'][0], info['album'][0])
            self.task_list.append(Video.Task(info['video'][1], full_path, info['video'][0], info['album'][1].cover))
            task_list.append((info['album'][1].aid, info['album'][1].name))

        task_list = list(set(task_list))
        return task_list

    def load_exist(self, output):
        """
        输出缓存中已经存在的视频编号
        区分乐观策略与悲观策略
        :param output: 输出路径
        :return: 乐观列表， 悲观列表
        """
        all_video_list = []
        positive_list = []
        negative_list = []
        base_path = os.path.abspath(output)

        for info in self.info_list:
            all_video_list.append(info['album'][1].aid)
            video_path = os.path.join(base_path, info['obj'][0], info['album'][0], '{}.mp4'.format(info['video'][0]))
            if os.path.exists(video_path):
                positive_list.append(info['album'][1].aid)
            else:
                negative_list.append(info['album'][1].aid)

        all_video_list = set(all_video_list)
        positive_list = list(set(positive_list))
        negative_list = list(all_video_list - set(negative_list))

        """
        生成策略在于
        乐观列表：Album下存在视频即认为存在
        悲观列表：Album下所有视频存在才存在
        """

        return positive_list, negative_list

    def pull_all(self, show_process=True, no_repeat=True):
        """
        批量开始下载任务
        :param show_process: 是否显示下载进度信息
        :param no_repeat: 是否重复下载
        :return: 完成下载的av号列表
        """
        av_list = []
        tot = len(self.task_list)
        this = 0
        for task in self.task_list:
            this += 1
            print("downloading video %.0f of %.0f"%(this, tot))
            av_list.append(task.start(show_process, no_repeat))
        av_list = list(set(av_list))
        return av_list
