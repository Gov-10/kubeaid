from datetime import timedelta 
from temporalio import workflow
from temporalio.common import RetryPolicy
with workflow.unsafe.imports_passed_through():
    from activities import k8s_worker, http_worker, smoke_worker
import os, json, httpx
from dotenv import load_dotenv
load_dotenv()

@workflow.defn(name="kubeWorflow")
class kubeWorflow:
    @workflow.run
    async def run(self, data:dict)-> str:
        custom_retry =RetryPolicy(initial_interval=timedelta(seconds=1), backoff_coefficient=2.0, maximum_interval=timedelta(seconds=30), maximum_attempts= 5, non_retryable_error_types=["ValueError"])
        for step in data.playbook["steps"]:
            if step["type"] == "scale":
                pass #schema fix, call k8s activity
            if step["type"] == "health_check":
                pass #schema fix, call http_worker
            if step["type"] == "smoke_test":
                pass #schemafix, call smoke_worker
            #TODO: combine the total result
        #TODO: return combined result (will be pushed to aggregator service)


