# evaluation/evaluator.py

import json
import os
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    GEval,
    TaskCompletionMetric,
    ArgumentCorrectnessMetric,
    ToolCorrectnessMetric,
    StepEfficiencyMetric,
    PlanAdherenceMetric
)
from google import genai
from google.genai import types
from dotenv import load_dotenv
from deepeval.models import DeepEvalBaseLLM
load_dotenv()

class GeminiModel(DeepEvalBaseLLM):
    def __init__(
        self,
        model_name: str = "gemini-flash-latest",
        temperature: float = 0.0,
        api_key: str | None = None,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=self.api_key)

    def load_model(self):
        # For API-based models, you can just return the client itself
        return self.client

    def generate(self, prompt: str) -> str:
        client = self.load_model()
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
            ),
        )
        return response.text

    async def a_generate(self, prompt: str) -> str:
        # DeepEval expects this in some async contexts
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return self.model_name

# Try to configure DeepEval with custom Gemini model
try:
    gemini_eval_model = GeminiModel(
        model_name="gemini-flash-latest",
        temperature=0.0,
    )
    
    print("✅ DeepEval configured with custom Gemini model")
except Exception as config_error:
    print(f"⚠️  DeepEval custom model configuration failed: {config_error}")
    print("   Using DeepEval default models for evaluation")


def evaluate_run(run_trace: dict) -> dict:

    print("\n" + "=" * 60)
    print("📊 [DeepEval] Starting evaluation...")
    print("=" * 60)

    query = run_trace["query"]
    report = json.dumps(run_trace["report"])
    execution_log = run_trace.get("execution_log", [])
    plan = run_trace.get("plan", {})

    print(f"  📝 Query: {query}")
    print(f"  📄 Report length: {len(report)} chars")
    print(f"  📋 Execution log entries: {len(execution_log)}")

    # ✅ FIX: Convert google_results to list of strings for context
    google_results = run_trace.get("google_results", [])
    
    # Convert each result to a string representation
    context_list = []
    for result in google_results:
        if isinstance(result, dict):
            # Convert dict to a readable string
            context_list.append(json.dumps(result))
        elif isinstance(result, str):
            context_list.append(result)
        else:
            context_list.append(str(result))
    
    print(f"  📚 Context items: {len(context_list)}")

    # ✅ FIX: Pass context as list of strings, not a single JSON string
    test_case = LLMTestCase(
        input=query,
        actual_output=report,
        context=context_list  # ✅ Changed from json.dumps() to list
    )

    # 1️⃣ Business Quality
    print("\n  🔄 [1/6] Measuring Business Quality...")
    business_metric = GEval(
        name="Business Quality",
        criteria="""
        Evaluate:
        - Strategic insight
        - Market analysis depth
        - Logical structure
        - Actionable recommendations
        """,
        model=gemini_eval_model  # ✅ Use custom Gemini model
    )
    business_metric.measure(test_case)
    print(f"  ✅ Business Quality:        {business_metric.score} | reason: {business_metric.reason}")

    # 2️⃣ Task Completion
    print("  🔄 [2/6] Measuring Task Completion...")
    task_metric = TaskCompletionMetric(
        model=gemini_eval_model  # ✅ Use custom Gemini model
    )
    task_metric.measure(test_case)
    print(f"  ✅ Task Completion:          {task_metric.score} | reason: {task_metric.reason}")

    # 3️⃣ Argument Correctness
    print("  🔄 [3/6] Measuring Argument Correctness...")
    argument_metric = ArgumentCorrectnessMetric(
        model=gemini_eval_model  # ✅ Use custom Gemini model
    )
    argument_metric.measure(test_case)
    print(f"  ✅ Argument Correctness:     {argument_metric.score} | reason: {argument_metric.reason}")

    # 4️⃣ Tool Correctness
    print("  🔄 [4/6] Measuring Tool Correctness...")
    tool_metric = ToolCorrectnessMetric(
        model=gemini_eval_model  # ✅ Use custom Gemini model
    )
    tool_metric.measure(test_case)
    print(f"  ✅ Tool Correctness:         {tool_metric.score} | reason: {tool_metric.reason}")

    # 5️⃣ Step Efficiency
    print("  🔄 [5/6] Measuring Step Efficiency...")
    step_metric = StepEfficiencyMetric(
        model=gemini_eval_model  # ✅ Use custom Gemini model
    )
    step_metric.measure(test_case)
    print(f"  ✅ Step Efficiency:          {step_metric.score} | reason: {step_metric.reason}")

    # 6️⃣ Plan Adherence
    print("  🔄 [6/6] Measuring Plan Adherence...")
    plan_metric = PlanAdherenceMetric(
        model=gemini_eval_model  # ✅ Use custom Gemini model
    )
    plan_metric.measure(test_case)
    print(f"  ✅ Plan Adherence:           {plan_metric.score} | reason: {plan_metric.reason}")

    results = {
        "business_quality": {"score": business_metric.score, "reason": business_metric.reason},
        "task_completion": {"score": task_metric.score, "reason": task_metric.reason},
        "argument_correctness": {"score": argument_metric.score, "reason": argument_metric.reason},
        "tool_correctness": {"score": tool_metric.score, "reason": tool_metric.reason},
        "step_efficiency": {"score": step_metric.score, "reason": step_metric.reason},
        "plan_adherence": {"score": plan_metric.score, "reason": plan_metric.reason},
    }

    print("\n" + "=" * 60)
    print("📊 [DeepEval] Final metrics summary:")
    print("=" * 60)
    for name, data in results.items():
        print(f"  {name:30s} → score: {data['score']}")
    print("=" * 60 + "\n")

    return results
