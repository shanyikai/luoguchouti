import json
import random
import webbrowser

from typing import List, Dict, Set, Union


# 按照 & 或者 | 的方式将 problems 合并为一个集合
def get_from_set(problems: List[List[str]], type_name: str) -> Set[str]:
    res: Set[str] = {"None"}
    for p in problems:
        if "None" in res:  # 第一项
            res = set(p)
        else:
            if type_name == 'or':
                res = res | set(p)  # 并集
            else:
                res = res & set(p)  # 交集
    return res


# 打开 problems/type_name/file_name.json, 并获取键为 id_name 项的值
def get_from_file(type_name: str, file_name: str, id_name: Union[int, str]) -> List[str]:
    with open(f'problems/{type_name}/{file_name}.json', 'r') as f:
        return json.load(f)[str(id_name)]


# 对列表中的每一项进行处理
def deal(data: Dict[str, Union[str, List[str], List[int], List[List[int]]]]):
    # 获取 _data[key], 如果为字符串, 返回 default, 否则返回 _data[key]
    # 用于处理 "all"
    def get(_data, key: str, default: Union[List[int], List[str]]) -> Union[List[int], List[str]]:
        if type(_data[key]) is str:
            return default
        else:
            return _data[key]

    tmp = []
    types: List[str] = get(data, 'type', ['P', 'B', 'CF', 'SP', 'AT', 'UVA'])
    for type_name in types:
        # 处理难度 difficulty
        difficulties = get(data, 'difficulty', list(range(7+1)))
        temp = []
        for difficulty in difficulties:
            temp.append(get_from_file(type_name, 'difficulty', difficulty))
        res = get_from_set(temp, 'or')

        # 处理不含有的标签 not
        temp = []
        for t in data['not']:
            temp2 = []
            for tag in t:
                temp2.append(get_from_file(type_name, 'tag', tag))
            temp.append(list(get_from_set(temp2, 'and')))
        temp3 = get_from_set(temp, 'or')
        res = res - temp3

        # 处理含有的标签 tag
        # 如果 data['tag'] 是 str 无需任何处理
        if not type(data['tag']) is str:
            temp = []
            for t in data['tag']:
                temp2 = []
                for tag in t:
                    temp2.append(get_from_file(type_name, 'tag', tag))
                temp.append(list(get_from_set(temp2, 'and')))
            temp3 = get_from_set(temp, 'or')
            res = res & temp3

        tmp.append(list(res))
    return list(get_from_set(tmp, 'or'))


# 在 problem_list 中随机抽取 count 个题目
# 如果 auto_open 为 True, 自动在浏览器里打开
def randomly_select(problem_list: List[str], auto_open: bool = False, count: int = 1) -> Union[str, List[str]]:
    if auto_open:
        problem = random.choice(problem_list)
        webbrowser.open(f'https://www.luogu.com.cn/problem/{problem}')
        return problem
    result = random.choices(problem_list, k=count)
    result.sort()
    return result


def main():
    file_name = input('请输入文件名: ')
    with open(f'data/{file_name}.json', 'r') as f:
        method = json.load(f)
    temp = []
    for i in method:
        temp.append(deal(i))
    result = list(get_from_set(temp, 'or'))

    if len(result) == 0:
        print('没有符合条件的题目!')
        return

    while True:
        a = input()
        if a == 'quit':
            break
        try:
            if int(a) > 0:
                if int(a) > len(result):
                    print('没有这么多题目!')
                    print(randomly_select(result, count=len(result)))
                else:
                    print(randomly_select(result, count=int(a)))
            else:
                print(randomly_select(result, auto_open=True))
        except:
            print(randomly_select(result, auto_open=True))


if __name__ == '__main__':
    main()
