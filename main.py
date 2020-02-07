import time
from feed_video_lucid import feedlucid_main
from feed_video_lincoln import feedLincoin_main
from feed_video_madoff import feedMadoff_main


def main():
    print("===== Start feeding Video Data =====")
    time.sleep(3)
    feedlucid_main()
    time.sleep(3)
    feedLincoin_main()
    time.sleep(3)
    feedMadoff_main()
    time.sleep(3)
    print("===== Finish feeding Video Data =====")




if __name__ == '__main__':
    main()