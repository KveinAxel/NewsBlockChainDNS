from fastapi import FastAPI
import re

app = FastAPI()
superNodes = dict()

# ip reg
pattern = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')


@app.post("/node")
async def node(ip: str):
    # check ip
    if pattern.search(ip):
        res = sorted(superNodes.items(), key=lambda x: x[1])
        if len(res):
            res = res[0][0]
            superNodes[res] = superNodes[res] + 1
            # request superNode to save ip
            return {"ip": res}
        else:
            return {"error": "there is no super node left"}
    else:
        return {"error": "the ip format is wrong"}


@app.post("/superNode")
async def superNode(ip: str):
    # check ip
    if pattern.search(ip):
        if ip not in superNodes:
            superNodes[ip] = 0
            return {"success": "inserted successfully"}
        else:
            return {"error": "the ip has been super node, please don't do it again"}
    else:
        return {"error": "the ip format is wrong"}


@app.post("/broadcast")
async def broadcast(block: str):
    for key in superNodes.keys():
        # request the block to superNodes
        pass
