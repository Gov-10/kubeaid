import asyncio, os, json
from kafka import KafkaConsumer
from temporalio.client import Client
from dotenv import load_dotenv
from workflows import kubeWorkflow
load_dotenv()

async def main():
    client = await Client.connect(os.getenv("TEMPORAL_URL"))
    consumer = KafkaConsumer("execution-send", bootstrap_servers= os.getenv("BOOTSTRAP_SERVER"), group_id="execution-group", value_deserializer= lambda i: json.loads(i.decode()))
    await consumer.start()
    try:
        async for msg in consumer:
            data = msg.value 
            exec_data = {} #TODO: DB se fetch karo
            await client.start_workflow(KafkaConsumer.run(), {"template_id": data["template_id"], "task_id": data["task_id"], "task": exec_data}, id=f"kube-task-{data['task_id']}",task_queue="kube-tasks")
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())

