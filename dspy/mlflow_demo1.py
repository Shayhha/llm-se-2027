import os

import dspy
import mlflow
import mlflow.dspy

mlflow.set_tracking_uri("http://127.0.0.1:5000/")
mlflow.set_experiment("deploy_dspy_program")

# lm = dspy.LM("openai/gpt-4o-mini")
# Set XAI_API_KEY in your environment (see .env.example); never hardcode keys.
dspy.configure(lm=dspy.LM('xai/grok-3-mini', api_key=os.environ['XAI_API_KEY']))

mlflow.dspy.autolog()

# dspy.settings.configure(lm=lm)

class MyProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.cot = dspy.ChainOfThought("question -> answer")

    def forward(self, messages: list[dict[str, str]]):
        return self.cot(question=messages[0]["content"])

dspy_program = MyProgram()

with mlflow.start_run():
    mlflow.dspy.log_model(
        dspy_program,
        "dspy_program",
        input_example={"messages": [{"role": "user", "content": "What is LLM agent?"}]},
        task="llm/v1/chat",
    )
    dspy_program(
        messages=[{"role": "user", "content": "How can I learn about DSPy?"}]
    )