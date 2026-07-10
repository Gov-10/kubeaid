import os, asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import kubeWorkflow
from activities import k8s_worker, http_worker, smoke_worker
from dotenv import load_dotenv
load_dotenv()
async def main():
    client = await Client.connect(os.getenv("TEMPORAL_URL"))
    worker = Worker(client, task_queue="kube-tasks", workflows=[kubeWorkflow], activities=[k8s_worker, http_worker, smoke_worker])
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
