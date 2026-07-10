from temporalio import activity
import httpx
class ExecuteInput:
    def __init__(self, task_id: str, template_id: str, task: str):
        self.task_id = task_id
        self.template_id = template_id
        self.task = task

class CustomNetworkError(Exception):
    def __init__(self, message:str):
        self.message= message

@activity.defn(name="k8s_worker")
async def k8s_worker(data:dict)-> str:
    with httpx.AsyncClient() as client:
        try:
            resp = await client.post(k8s_url, json=data, timeout=3)
            return resp
        except Exception as e:
            raise CustomNetworkError(str(e))

@activity.defn(name="http_worker")
async def http_worker(data:dict)-> str:
    with httpx.AsyncClient() as client:
        try:
            resp = await client.post(http_url, json=data, timeout=3)
            return resp
        except Exception as e:
            raise CustomNetworkError(str(e))

@activity.defn(name="smoke_worker")
async def smoke_worker(data:dict)-> str:
    with httpx.AsyncClient() as client:
        try:
            resp = await client.post(smoke_url, json=data, timeout=3)
            return resp
        except Exception as e:
            raise CustomNetworkError(str(e))


    




