from flask import Flask, request
import logging
import subprocess
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # 获取请求的数据
    data = request.json

    # 打印或处理数据
    REPO_DIR = "/root/" + data.repository.name
    logging.debug("Received webhook data:", data.repository.name)

    script_path = REPO_DIR + "/start.sh"
    work_dir = REPO_DIR

    # 切换工作目录并执行脚本
    try:
        os.chdir(work_dir)
        subprocess.run(['sh', script_path], check=True)
        logging.debug("Successfully executed the script.")
    except Exception as e:
        logging.debug(f"Error executing the script: {e}")

    return 'Success', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)