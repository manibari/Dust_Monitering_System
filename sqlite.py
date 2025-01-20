import os
import pandas as pd
import sqlite3
import schedule
import time
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 資料庫設定
db_file = "dust_data.db"
table_name = "dust_data"
watch_folder = "data"  # 替換為您的 CSV 資料夾路徑


# 定義檔案監控處理

class NewCSVHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".csv"):
            return

        print(f"檔案已生成：{event.src_path}")
        try:
            # 匯入新檔案資料
            df = pd.read_csv(event.src_path)
            conn = sqlite3.connect(db_file)
            df.to_sql(table_name, conn, if_exists="append", index=False)
            conn.close()
            print("新資料已匯入資料庫！")
        except Exception as e:
            print(f"匯入資料時發生錯誤：{e}")


# 清理舊 CSV 文件


def cleanup_csv_files(folder, keep_count=10):
    """清理資料夾內的舊 CSV 文件，只保留最新的 `keep_count` 個"""
    try:
        # 獲取資料夾內的所有 CSV 文件，按修改時間排序
        csv_files = glob.glob(os.path.join(folder, "*.csv"))
        csv_files.sort(key=os.path.getmtime, reverse=True)

        # 判斷是否超出保留數量
        if len(csv_files) > keep_count:
            old_files = csv_files[keep_count:]  # 超過的文件
            for file in old_files:
                os.remove(file)
                print(f"已刪除舊文件：{file}")
        else:
            print("沒有需要刪除的文件，所有文件均在保留範圍內。")
    except Exception as e:
        print(f"清理舊文件時發生錯誤：{e}")


# 啟動檔案監控
event_handler = NewCSVHandler()
observer = Observer()
observer.schedule(event_handler, watch_folder, recursive=False)
observer.start()

try:
    print(f"監控資料夾：{watch_folder}")
    while True:
        pass  # 持續監控
except KeyboardInterrupt:
    observer.stop()
observer.join()

# 添加清理任務
schedule.every().day.at("03:08").do(
    cleanup_csv_files, folder=watch_folder, keep_count=10)

# 主循環添加調度執行
try:
    print(f"監控資料夾：{watch_folder}")
    while True:
        schedule.run_pending()  # 執行定時任務
        time.sleep(1)  # 每秒檢查一次
except KeyboardInterrupt:
    observer.stop()
observer.join()
