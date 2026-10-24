import os

import requests
import time
import zipfile

# MinerU 需要自己的 API Token：https://mineru.net 控制台获取
# 不要把 token 写进代码，也不要提交到仓库
API_KEY = os.environ.get("MINERU_API_KEY", "")
# PDF 必须能被 MinerU 服务端下载到，这里填你自己的对象存储前缀
PDF_BASE_URL = os.environ.get("MINERU_PDF_BASE_URL", "")


def _headers():
    if not API_KEY:
        raise RuntimeError("缺少环境变量 MINERU_API_KEY")
    return {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + API_KEY,
    }


def get_task_id(file_name):
    url = 'https://mineru.net/api/v4/extract/task'
    if not PDF_BASE_URL:
        raise RuntimeError("缺少环境变量 MINERU_PDF_BASE_URL（PDF 的公网可访问前缀）")
    pdf_url = PDF_BASE_URL.rstrip('/') + '/' + file_name
    data = {
        'url': pdf_url,
        'is_ocr': True,
        'enable_formula': False,
    }

    res = requests.post(url, headers=_headers(), json=data)
    print(res.status_code)
    print(res.json())
    print(res.json()["data"])
    task_id = res.json()["data"]['task_id']
    return task_id


def get_result(task_id):
    url = 'https://mineru.net/api/v4/extract/task/' + task_id

    while True:
        res = requests.get(url, headers=_headers())
        result = res.json()["data"]
        print(result)
        state = result.get('state')
        err_msg = result.get('err_msg', '')
        # 如果任务还在进行中，等待后重试
        if state in ['pending', 'running']:
            print("任务未完成，等待5秒后重试...")
            time.sleep(5)
            continue
        # 如果有错误，输出错误信息
        if err_msg:
            print("任务出错: " + err_msg)
            return
        # 如果任务完成，下载文件
        if state == 'done':
            full_zip_url = result.get('full_zip_url')
            if full_zip_url:
                local_filename = task_id + ".zip"
                print("开始下载: " + full_zip_url)
                r = requests.get(full_zip_url, stream=True)
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print("下载完成，已保存到: " + local_filename)
                # 下载完成后自动解压
                unzip_file(local_filename)
            else:
                print("未找到 full_zip_url，无法下载。")
            return
        # 其他未知状态
        print("未知状态: " + str(state))
        return


# 解压zip文件的函数
def unzip_file(zip_path, extract_dir=None):
    """
    解压指定的zip文件到目标文件夹。
    :param zip_path: zip文件路径
    :param extract_dir: 解压目标文件夹，默认与zip同名
    """
    if extract_dir is None:
        extract_dir = zip_path.rstrip('.zip')
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("已解压到: " + extract_dir)


if __name__ == "__main__":
    file_name = '【财报】中芯国际：中芯国际2024年年度报告.pdf'
    task_id = get_task_id(file_name)
    print('task_id:', task_id)
    get_result(task_id)
