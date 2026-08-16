import csv
import json
from collections import defaultdict


def load_data():

    with open("results.csv", encoding="utf-8") as f:
        results = list(csv.DictReader(f))

    with open("scenarios.json", encoding="utf-8") as f:
        scenarios = json.load(f)

    scenario_map = {
        str(s["id"]): s
        for s in scenarios
    }

    for result in results:

        scenario = scenario_map[result["scenario"]]

        result["category"] = scenario["category"]
        result["difficulty"] = scenario["difficulty"]
        result["expected_tools"] = scenario["expected_tools"]

        result["success"] = (
            result.get("success", "").lower() == "true"
        )

        result["has_error"] = bool(
            result.get("error")
        )

        if result.get("latency"):
            result["latency"] = float(
                result["latency"]
            )
        else:
            result["latency"] = None

        if result.get("tools"):

            try:
                result["tools"] = json.loads(
                    result["tools"].replace("'", '"')
                )
            except json.JSONDecodeError:
                result["tools"] = []

        else:
            result["tools"] = []

    return results


def calculate_statistics(results):

    stats = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
            "errors": 0,
            "latencies": [],
            "tool_expected": 0,
            "tool_called": 0,
            "multistep_total": 0,
            "multistep_correct": 0,
            "multistep_expected_calls": 0,
            "multistep_correct_calls": 0
        }
    )

    for r in results:

        model = r["model"]

        stats[model]["total"] += 1


        if r["success"]:
            stats[model]["correct"] += 1


        if r["has_error"]:
            stats[model]["errors"] += 1


        if r["latency"] is not None:
            stats[model]["latencies"].append(
                r["latency"]
            )

        expected = r["expected_tools"]

        if expected:

            stats[model]["tool_expected"] += 1

            if r["tools"]:
                stats[model]["tool_called"] += 1

        if len(expected) > 1:

            stats[model]["multistep_total"] += 1

            if r["success"]:
                stats[model]["multistep_correct"] += 1

            stats[model]["multistep_expected_calls"] += len(
                expected
            )

            expected_set = {
                json.dumps(
                    x,
                    sort_keys=True
                )
                for x in expected
            }

            predicted_set = {
                json.dumps(
                    x,
                    sort_keys=True
                )
                for x in r["tools"]
            }

            correct = (
                expected_set
                &
                predicted_set
            )

            stats[model]["multistep_correct_calls"] += len(
                correct
            )

    return stats


def build_summary(stats):

    summary = []

    for model, s in stats.items():

        accuracy = (
            s["correct"]
            /
            s["total"]
            if s["total"]
            else 0
        )

        if s["latencies"]:

            average_latency = (
                sum(s["latencies"])
                /
                len(s["latencies"])
            )

        else:
            average_latency = 0

        error_rate = (
            s["errors"]
            /
            s["total"]
            if s["total"]
            else 0
        )

        tool_call_rate = (
            s["tool_called"]
            /
            s["tool_expected"]
            if s["tool_expected"]
            else 0
        )

        multistep_accuracy = (
            s["multistep_correct"]
            /
            s["multistep_total"]
            if s["multistep_total"]
            else 0
        )

        multistep_tool_accuracy = (
            s["multistep_correct_calls"]
            /
            s["multistep_expected_calls"]
            if s["multistep_expected_calls"]
            else 0
        )

        summary.append({

            "model": model,

            "accuracy":
                round(accuracy, 4),

            "average_latency":
                round(average_latency, 3),

            "error_rate":
                round(error_rate, 4),

            "tool_call_rate":
                round(tool_call_rate, 4),

            "multistep_accuracy":
                round(multistep_accuracy, 4),

            "multistep_tool_accuracy":
                round(multistep_tool_accuracy, 4)

        })

    return summary


def save_summary(summary):

    filename = "benchmark_statistics.csv"

    fieldnames = [
        "model",
        "accuracy",
        "average_latency",
        "error_rate",
        "tool_call_rate",
        "multistep_accuracy",
        "multistep_tool_accuracy"
    ]

    with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(summary)

    print(
        f"\nStatistics saved to {filename}"
    )


if __name__ == "__main__":

    results = load_data()

    stats = calculate_statistics(
        results
    )

    summary = build_summary(
        stats
    )

    save_summary(
        summary
    )