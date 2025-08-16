import shutil

if __name__ == "__main__":
    shutil.make_archive("ttfunds", "zip", ".")
    print("打包完成: ttfunds.zip")