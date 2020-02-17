# coding=utf-8
import BiliUtil
import time
import sys
import MySESS

# ex_list = [60100181,
#            53057614,
#            41761079,
#            41199057,
#            40614787,
#            40134400,
#            39859420,
#            39455691,
#            39178654,
#            36190973,
#            35882922,
#            35880672,
#            35699264,
#            35704348,
#            35388343,
#            35335486,
#            35273930,
#            35216724,
#            35140942,
#            35101586,
#            19163944,
#            19095088,
#            18626501,
#            18284515,
#            9415557,
#            9237260,
#            9123295,
#            8980806,
#            8823787,
#            8696945,
#            60100181,
#            53057614,
#            41761079,
#            41199057,
#            40614787,
#            40134400,
#            39859420,
#            39455691,
#            39178654,
#            36190973,
#            35882922,
#            35880672,
#            35699264,
#            35704348,
#            35388343,
#            35335486,
#            35273930,
#            35216724,
#            35140942,
#            35101586,
#            19163944,
#            19095088,
#            18626501,
#            18284515,
#            9415557,
#            9237260,
#            9123295,
#            8980806,
#            8823787,
#            8696945,
#            8548131,
#            8011709,
#            7983364,
#            7890781,
#            7801685,
#            7672336,
#            7569463,
#            7488144,
#            7321406,
#            6842310,
#            6834956,
#            5398247,
#            4828773,
#            8548131,
#            8011709,
#            7983364,
#            7890781,
#            7801685,
#            7672336,
#            7569463,
#            7488144,
#            7321406,
#            6842310,
#            6834956,
#            5398247,
#            4828773,
#            80487424,
#            18211445,
#            82449193]
ex_list = []

video_cache = r'D:\Testv2'
cookie = MySESS.mysess

# 设置代理信息
# BiliUtil.Config.HTTP_PROXY = 'http://127.0.0.1:8888'
# BiliUtil.Config.HTTPS_PROXY = 'http://127.0.0.1:8888'

if __name__ == '__main__':
    # 初始化过滤器
    # 设置视频质量限制
    quality = [BiliUtil.Config.Quality.V1080P,
               BiliUtil.Config.Quality.V1080Px,
               BiliUtil.Config.Quality.V1080P60,
               BiliUtil.Config.Quality.V720P60,
               BiliUtil.Config.Quality.V720P]
    # length = [40, 600]  # 设置视频长度
    # ratio = [1, 2]  # 设置视频比例，只保留横屏
    video_filter = BiliUtil.Filter(quality=quality)

    # 扫描指定用户并下载
    # 模仿该方式，你也可以下载用户某个频道下的全部视频

    while True:
        try:
            # set user here!
            user = BiliUtil.User('11336264')
            fetcher = BiliUtil.Fetcher(user)
            av_list = fetcher.fetch_all(cookie, BiliUtil.Config.SET_AS_CODE)
            #print(av_list)
            positive_list, negative_list = fetcher.load_exist(video_cache)
            exclude_list = positive_list + ex_list
            task_list = fetcher.load_task(video_cache, exclude_list, video_filter, keyword_filter='录播')
            for i in task_list:
                print('av%s: %s'%(i[0],i[1]))
            download_list = fetcher.pull_all()
            print('完成{}个视频下载：{}'.format(len(download_list), download_list))
            break
        except BiliUtil.Util.tools.RunningError:
            print("retry!!! @RunningError")
            print(sys.exc_info())
            time.sleep(600)
            print("wait Done!")
            continue
        except Exception as e:
            exc_info = sys.exc_info()
            print("retry!!! on %s" % (str(e)))
            time.sleep(600)
            print("wait Done!")
            continue
