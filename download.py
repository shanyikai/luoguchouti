import os
import json
import shutil

from typing import List, Dict, Union
from urllib.request import urlopen

from bs4 import BeautifulSoup
from parse import parse

types: List[str] = ['P', 'B', 'CF', 'SP', 'AT', 'UVA']  # 题库类型
difficulties: List[int] = list(range(7+1))  # 难度列表
tags: List[int] = list(range(1, 394+1))  # 标签列表


# 船舰所需要的文件夹
def create():
    def make(folder):
        try:
            os.mkdir(folder)
        except:
            pass

    make('data')
    make('problems')
    for type_name in types:
        make(f'problems/{type_name}')
        make(f'problems/{type_name}/difficulty')
        make(f'problems/{type_name}/tag')


# 下载 luogu_url 的全部题目, 并以题目编号的形式返回, luogu_url 必须以 page= 结尾
# method 为 1 代表获得题目编号, method 为 2 代表获得题目名称
def download(luogu_url: str, method: int = 1) -> Union[List[str], Dict[str, str]]:
    page: int = 1
    result: Dict[str, str] = {}
    while True:
        new_url = luogu_url + str(page)
        print(f'正在爬取 {new_url}...')
        url = urlopen(new_url)
        html = bytes.decode(url.read())
        soup = BeautifulSoup(html, 'lxml')
        problems = soup.select('ul li')  # 第 page 页的问题列表
        if not problems:
            break  # 第 page 页没有问题, 全部下载完成
        for p in problems:
            # 解析这一页的所有题目 problem_id 代表题目编号, problem_name 代表题目名称
            problem = parse('<li>{problem_id}\xa0<a href="{problem_id2}">{problem_name}</a></li>', str(p))
            result[problem['problem_id']] = problem['problem_name']
        page += 1
    if method == 1:
        return list(result.keys())
    else:
        return result


def main():
    # 遍历每一种题库, 下载题目
    for type_name in types:
        # 下载题目编号与题目名称的对应关系
        url = f'https://www.luogu.com.cn/problem/list?type={type_name}&page='
        result = download(url, 2)
        with open(f'problems/{type_name}/name.json', 'w', encoding='utf-8') as f:
            json.dump(result, f)
        print()

        for difficulty in difficulties:
            # 下载题库中难度为 difficulty 的题目
            url = f'https://www.luogu.com.cn/problem/list?type={type_name}&difficulty={difficulty}&page='
            result = download(url)
            with open(f'problems/{type_name}/difficulty/{difficulty}.json', 'w') as f:
                json.dump(result, f)
            print()

        for tag in tags:
            # 下载题库中含有标签 tag 的题目
            url = f'https://www.luogu.com.cn/problem/list?type={type_name}&tag={tag}&page='
            result = download(url)
            with open(f'problems/{type_name}/tag/{tag}.json', 'w') as f:
                json.dump(result, f)
            print()


# 把相同题库下的所有标签(难度)合并到一个文件
def merge():
    for type_name in types:
        result: Dict[str, List[str]] = {}
        for difficulty in difficulties:
            with open(f'problems/{type_name}/difficulty/{difficulty}.json', 'r') as f:
                result[str(difficulty)] = json.load(f)
        with open(f'problems/{type_name}/difficulty.json', 'w') as f:
            json.dump(result, f)

        result = {}
        for tag in tags:
            with open(f'problems/{type_name}/tag/{tag}.json', 'r') as f:
                result[str(tag)] = json.load(f)
        with open(f'problems/{type_name}/tag.json', 'w') as f:
            json.dump(result, f)
        print(f'{type_name} 已完成!')


# 删除多余文件
def delete():
    for type_name in types:
        shutil.rmtree(f'problems/{type_name}/difficulty')
        shutil.rmtree(f'problems/{type_name}/tag')


if __name__ == '__main__':
    create()
    main()
    merge()
    delete()
