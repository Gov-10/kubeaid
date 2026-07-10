from datetime import timedelta 
from temporalio import workflow
from temporalio.common import RetryPolicy
with workflow.unsafe.imports_passed_through():
    from activities import k8s_worker, http_worker, smoke_worker

@workflow.defn(name="kubeWorflow")
class kubeWorflow:
    @workflow.run
    async def run(self, data:dict)-> str:
        custom_retry =RetryPolicy(initial_interval=timedelta(seconds=1), backoff_coefficient=2.0, maximum_interval=timedelta(seconds=30), maximum_attempts= 5, non_retryable_error_types=["ValueError"])
        pass 
        #TODO: TO be done later

