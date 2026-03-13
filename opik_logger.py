# utils/opik_logger.py

from opik import track

def push_metrics_to_opik(run_id: str, metrics: dict, latency: float):

    print("\n" + "-" * 60)
    print("🔭 [Opik] Pushing metrics to Opik/Comet...")
    print(f"  📌 Run ID:  {run_id}")
    print(f"  ⏱️  Latency: {latency:.2f}s")
    print("  📊 Metrics being pushed:")
    for name, data in metrics.items():
        score = data["score"] if isinstance(data, dict) else data
        print(f"     {name:30s} → {score}")

    try:
        with track(project_name="market-research-copilot") as exp:
            exp.log_parameters({
                "run_id": run_id
            })

            # Flatten scores for Opik (it expects simple numeric values)
            flat_metrics = {}
            for name, data in metrics.items():
                flat_metrics[name] = data["score"] if isinstance(data, dict) else data
            flat_metrics["latency_seconds"] = latency

            exp.log_metrics(flat_metrics)

        print("  ✅ [Opik] Metrics pushed successfully!")
    except Exception as e:
        print(f"  ❌ [Opik] Error pushing metrics: {e}")

    print("-" * 60 + "\n")