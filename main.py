import json
from typing import Dict, Tuple

from fastapi import FastAPI
import re
import requests

app = FastAPI()
superNodes: Dict[Tuple[str, int], int] = dict()

# IP的正则表达式
pattern = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')


# 请求成为普通节点
@app.get("/node")
async def node(url: str, port: int):
    # 检查IP是否合法
    if pattern.search(url):

        # 将超级节点排序
        res = sorted(superNodes.items(), key=lambda x: x[1])
        if len(res):

            # 取出负载最少的超级节点的url和port
            s_url = res[0][0][0]
            s_port = res[0][0][1]

            # 负载数加一
            superNodes[res[0][0]] = superNodes[res[0][0]] + 1

            # 请求参数
            params = {
                'url': url,
                'port': port,
            }

            # 将ip加入超级节点的ip列表
            r = requests.get("http://" + s_url + ":" + str(s_port) + "/network/saveIp", params=params)

            # 处理返回结果
            if r.status_code != 200:
                return {"code": 400, "message": "加入网络失败"}

            # 返回超级节点的IP
            return {"code": 200, "message": "加入网络成功", "data": {"url": s_url, "port": s_port}}
        else:
            return {"code": 400, "message": "无超级节点，无法加入区块网络"}
    else:
        return {"code": 400, "message": "IP地址格式异常"}


# 请求成为超级节点
@app.get("/superNode")
async def super_node(url: str, port: int):
    # todo 将原来的父节点中保存的普通节点删除（如果有的话）
    # 检查IP地址
    if pattern.search(url) and 0 < port <= 65536:

        # 加入节点，负载为0
        if (url, port) not in superNodes:
            superNodes[(url, port)] = 0
            params = {
                "url": url,
                "port": port
            }
            for key in superNodes.keys():
                r = requests.get("http://" + key[0] + ":" + str(key[1]) + "/network/deleteNode" + "?url=" + url + "&port=" + str(port))
            return {"code": 200, "message": "加入区块网络成功"}
        else:
            return {"code": 400, "message": "该IP已经成为超级节点，请勿重复添加"}
    else:
        return {"code": 400, "message": "IP地址格式异常"}


# 向超级节点广播区块
@app.get("/broadcast")
async def broadcast(block: str):
    # 构造参数
    params = {
        "block": block
    }
    for key in superNodes.keys():

        r = requests.get("http://" + key[0] + ":" + str(key[1]) + "/network/broadcastBlockBySuperNode", params)
        if r.status_code == 200:
            return {"code": 200, "message": "广播成功"}
        else:
            return {"code": 200, "message": "广播失败"}


# 向超级节点请求区块
@app.get("/getBlockChain")
async def broadcast():
    nth_max = 0
    block_max = ''
    for nodes in superNodes.keys():

        r = requests.get("http://" + nodes[0] + ":" + str(nodes[1]) + "/network/getBlock")
        if r.status_code == 200:
            j = json.loads(r.text)
            data = j['data']
            nth = int(data['nth'])
            block = data['block']
            if nth > nth_max:
                block_max = block

    if block_max == '':
        return {"code": 400, "message": "没有请求到数据"}
    else:
        return {"code": 200, "message": "成功请求到数据", "data": block_max}


# 向超级节点部分请求区块
@app.get("/getBlockChainPartly")
async def broadcast(key: str):
    nth_max = 0
    block = ''
    for nodes in superNodes.keys():
        params = {
            "key": key
        }
        r = requests.get("http://" + nodes[0] + ":" + str(nodes[1]) + "/network/getBlockPartly", params=params)
        if r.status_code == 200:
            j = json.loads(r.text)
            if j['nth'] > nth_max:
                block = j['block']

    if block == '':
        return {"code": 400, "message": "没有请求到数据"}
    else:
        return {"code": 200, "message": "成功请求到数据", "data": block}
