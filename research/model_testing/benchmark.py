import csv
import json
import os
import time

from dotenv import load_dotenv

from llm import LLM
from tools import Tools
from virtual_home import SmartHome

load_dotenv()

API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)


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

    def test_model(self, model):

        print(
            "Testing:",
            model
        )
        llm = LLM(
            model
        )

        home = SmartHome()

        tools = Tools(home)

        scenarios = self.load_scenarios()

        results = []

        for scenario in scenarios:

            print(
                "Scenario:",
                scenario["id"]
            )

            home.reset()

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

            try:

                response = llm.ask(

                    messages,

                    self.config,

                    tools.schema()

                )

                latency = (
                        time.time()
                        -
                        start
                )

                result = {

                    "model": model,

                    "scenario":
                        scenario["id"],

                    "latency":
                        round(latency, 3),

                    "success":
                        False

                }

                if response.tool_calls:

                    predicted_tools = []

                    for call in response.tool_calls:

                        name = call.function.name

                        args = json.loads(call.function.arguments)

                        predicted_tools.append(
                            {
                                "name": name,
                                "arguments": args,
                            }
                        )

                        tools.execute(
                            {
                                "function":
                                    {
                                        "name": name,
                                        "arguments": args
                                    }
                            }
                        )

                    result["tools"] = json.dumps(
                        predicted_tools,
                        ensure_ascii=False
                    )

                    expected = scenario["expected_tools"]

                    if self.normalize_tools(predicted_tools) == self.normalize_tools(expected):
                        result["success"] = True

                results.append(result)

            except Exception as e:

                results.append({

                    "model": model,

                    "scenario":
                        scenario["id"],

                    "error":
                        str(e)

                })

        return results

    @staticmethod
    def normalize_tools(tools):
        return sorted(
            tools,
            key=lambda x: x["name"]
        )

    def run(self):

        all_results = []

        for model in self.config["models"]:
            results = self.test_model(
                model
            )

            all_results.extend(
                results
            )

        self.save(
            all_results
        )

    def save(self, results):

        fields = set()

        for result in results:
            fields.update(result.keys())

        fields = list(fields)

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
