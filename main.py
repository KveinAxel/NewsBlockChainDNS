from fastapi import FastAPI
import re

app = FastAPI()
superNodes = dict()

# IP的正则表达式
pattern = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')


# 请求成为普通节点
@app.post("/node")
async def node(ip: str):

    # 检查IP是否合法
    if pattern.search(ip):

        # 将超级节点排序
        res = sorted(superNodes.items(), key=lambda x: x[1])
        if len(res):

            # 取出负载最少的节点
            res = res[0][0]

            # 负载数加一
            superNodes[res] = superNodes[res] + 1

            # TODO 请求超级节点以保存IP
            # 返回超级节点的IP
            return {"ip": res}
        else:
            return {"error": "无超级节点，无法加入区块网络"}
    else:
        return {"error": "IP地址格式异常"}


# 请求成为超级节点
@app.post("/superNode")
async def super_node(ip: str):

    # 检查IP地址
    if pattern.search(ip):

        # 加入节点，负载为0
        if ip not in superNodes:
            superNodes[ip] = 0
            return {"success": "加入区块网络成功"}
        else:
            return {"error": "该IP已经成为超级节点，请勿重复添加"}
    else:
        return {"error": "IP地址格式异常"}


# 向超级节点广播区块
@app.post("/broadcast")
async def broadcast(block: str):
    for key in superNodes.keys():
        # 向超级节点广播区块
        pass
