import csv
import json
import os
import time

from dotenv import load_dotenv

from llm import LLM
from tools import Tools
from virtual_home import SmartHome


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")


class Benchmark:

    def __init__(self):
        with open(
                "config.json",
                encoding="utf-8"
        ) as f:
            self.config = json.load(f)

    def load_scenarios(self):
        with open(
                self.config["benchmark"]["scenario_file"],
                encoding="utf-8"
        ) as f:
            return json.load(f)

    @staticmethod
    def normalize_tools(tools):
        normalized = []

        for tool in tools:
            normalized.append({
                "name": tool.get("name"),
                "arguments": tool.get("arguments", {})
            })

        return sorted(
            normalized,
            key=lambda x: (
                x["name"],
                json.dumps(
                    x["arguments"],
                    sort_keys=True,
                    ensure_ascii=False
                )
            )
        )

    @staticmethod
    def extract_tool_calls(response):

        if response is None:
            return []

        tool_calls = getattr(response, "tool_calls", None)

        if not tool_calls:
            return []

        predicted_tools = []

        for call in tool_calls:

            try:
                function = getattr(call, "function", None)

                if function is None:
                    continue

                name = getattr(function, "name", None)
                arguments = getattr(function, "arguments", None)

                if not name:
                    continue

                if arguments is None:
                    arguments = {}

                elif isinstance(arguments, str):

                    if arguments.strip():
                        try:
                            arguments = json.loads(arguments)
                        except json.JSONDecodeError:
                            arguments = {
                                "_invalid_arguments": arguments
                            }
                    else:
                        arguments = {}

                elif not isinstance(arguments, dict):
                    arguments = {
                        "_invalid_arguments": str(arguments)
                    }

                predicted_tools.append({
                    "name": name,
                    "arguments": arguments
                })

            except Exception:
                continue

        return predicted_tools

    def execute_tools(self, tools, predicted_tools):

        execution_errors = []

        for tool in predicted_tools:

            try:
                tools.execute({
                    "function": {
                        "name": tool["name"],
                        "arguments": tool["arguments"]
                    }
                })

            except Exception as e:
                execution_errors.append({
                    "tool": tool["name"],
                    "error": str(e)
                })

        return execution_errors

    def test_model(self, model):

        print("Testing:", model)

        results = []

        try:
            llm = LLM(model)
        except Exception as e:

            print(
                f"Failed to initialize model {model}: {e}"
            )

            return [{
                "model": model,
                "scenario": None,
                "success": False,
                "status": "initialization_error",
                "error": str(e)
            }]

        home = SmartHome()
        tools = Tools(home)
        scenarios = self.load_scenarios()

        for scenario in scenarios:

            scenario_id = scenario["id"]

            print(
                "Scenario:",
                scenario_id
            )

            try:
                home.reset()
            except Exception as e:

                results.append({
                    "model": model,
                    "scenario": scenario_id,
                    "success": False,
                    "status": "home_reset_error",
                    "error": str(e)
                })

                continue

            messages = [
                {
                    "role": "system",
                    "content": self.config["system_prompt"]
                },
                {
                    "role": "system",
                    "content":
                        "Текущее состояние дома:\n"
                        + json.dumps(
                            home.get_state(),
                            ensure_ascii=False,
                            indent=2
                        )
                },
                {
                    "role": "user",
                    "content": scenario["prompt"]
                }
            ]

            start = time.time()

            result = {
                "model": model,
                "scenario": scenario_id,
                "category": scenario.get("category"),
                "difficulty": scenario.get("difficulty"),
                "latency": None,
                "success": False,
                "status": None,
                "tools": "",
                "expected_tools": json.dumps(
                    scenario.get("expected_tools", []),
                    ensure_ascii=False
                ),
                "error": ""
            }

            try:

                response = llm.ask(
                    messages,
                    self.config,
                    tools.schema()
                )

            except Exception as e:

                result["latency"] = round(
                    time.time() - start,
                    3
                )

                result["status"] = "llm_error"
                result["error"] = str(e)

                results.append(result)

                print(
                    f"  ERROR: {e}"
                )

                continue

            result["latency"] = round(
                time.time() - start,
                3
            )

            try:

                predicted_tools = self.extract_tool_calls(
                    response
                )

            except Exception as e:

                result["status"] = "tool_parse_error"
                result["error"] = str(e)

                results.append(result)

                print(
                    f"  TOOL PARSE ERROR: {e}"
                )

                continue

            result["tools"] = json.dumps(
                predicted_tools,
                ensure_ascii=False
            )

            expected_tools = scenario.get(
                "expected_tools",
                []
            )

            if not predicted_tools:

                if expected_tools:

                    result["status"] = "no_tool"

                else:
                    result["status"] = "success"
                    result["success"] = True

                results.append(result)

                print(
                    f"  {result['status']}"
                )

                continue

            execution_errors = self.execute_tools(
                tools,
                predicted_tools
            )

            if execution_errors:

                result["status"] = "tool_execution_error"

                result["error"] = json.dumps(
                    execution_errors,
                    ensure_ascii=False
                )

                results.append(result)

                print(
                    f"  TOOL EXECUTION ERROR: "
                    f"{execution_errors}"
                )

                continue

            predicted_normalized = (
                self.normalize_tools(
                    predicted_tools
                )
            )

            expected_normalized = (
                self.normalize_tools(
                    expected_tools
                )
            )

            if predicted_normalized == expected_normalized:

                result["success"] = True
                result["status"] = "success"

            else:

                result["status"] = "wrong_tool"

            results.append(result)

            print(
                f"  {result['status']}"
            )

        return results

    def run(self):

        all_results = []

        for model in self.config["models"]:

            try:

                results = self.test_model(
                    model
                )

                all_results.extend(
                    results
                )

            except Exception as e:
                print(
                    f"CRITICAL ERROR for {model}: {e}"
                )

                all_results.append({
                    "model": model,
                    "scenario": None,
                    "success": False,
                    "status": "benchmark_error",
                    "error": str(e)
                })

        self.save(
            all_results
        )

        return all_results

    def save(self, results):
        fields = [
            "model",
            "scenario",
            "category",
            "difficulty",
            "latency",
            "success",
            "status",
            "tools",
            "expected_tools",
            "error"
        ]

        with open(
                self.config["benchmark"]["results_file"],
                "w",
                newline="",
                encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fields,
                extrasaction="ignore"
            )

            writer.writeheader()

            writer.writerows(
                results
            )


if __name__ == "__main__":
    Benchmark().run()