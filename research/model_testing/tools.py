class Tools:

    def __init__(self, home):
        self.home = home

    @staticmethod
    def schema():

        room_schema = {
            "type": "string",
            "description": "Комната, в которой находится устройство.",
            "enum": [
                "living_room"
            ]
        }

        return [

            {
                "type": "function",
                "function": {
                    "name": "turn_on_light",
                    "description": "Включить свет.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "room": room_schema
                        },
                        "required": ["room"],
                        "additionalProperties": False
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "turn_off_light",
                    "description": "Выключить свет.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "room": room_schema
                        },
                        "required": ["room"],
                        "additionalProperties": False
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "set_light_brightness",
                    "description": "Установить яркость света.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "room": room_schema,
                            "brightness": {
                                "type": "integer",
                                "description": "Яркость в процентах.",
                                "minimum": 0,
                                "maximum": 100
                            }
                        },
                        "required": [
                            "room",
                            "brightness"
                        ],
                        "additionalProperties": False
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "set_temperature",
                    "description": "Установить температуру термостата.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "temperature": {
                                "type": "number",
                                "minimum": 16,
                                "maximum": 30
                            }
                        },
                        "required": [
                            "temperature"
                        ],
                        "additionalProperties": False
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "turn_on_humidifier",
                    "description": "Включить увлажнитель.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "turn_off_humidifier",
                    "description": "Выключить увлажнитель.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "set_target_humidity",
                    "description": "Установить целевую влажность.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "humidity": {
                                "type": "integer",
                                "minimum": 20,
                                "maximum": 80
                            }
                        },
                        "required": [
                            "humidity"
                        ],
                        "additionalProperties": False
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "turn_on_air_purifier",
                    "description": "Включить очиститель воздуха.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "turn_off_air_purifier",
                    "description": "Выключить очиститель воздуха.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                }
            }

        ]

    def execute(self, tool_call):

        name = tool_call["function"]["name"]
        args = tool_call["function"]["arguments"]

        if name == "turn_on_light":
            return self.home.execute({
                "device": "light",
                "action": "on",
                "room": args["room"]
            })

        elif name == "turn_off_light":
            return self.home.execute({
                "device": "light",
                "action": "off",
                "room": args["room"]
            })

        elif name == "set_light_brightness":
            return self.home.execute({
                "device": "light",
                "action": "brightness",
                "room": args["room"],
                "value": args["brightness"]
            })

        elif name == "set_temperature":
            return self.home.execute({
                "device": "thermostat",
                "action": "set",
                "value": args["temperature"]
            })

        elif name == "turn_on_humidifier":
            return self.home.execute({
                "device": "humidifier",
                "action": "on"
            })

        elif name == "turn_off_humidifier":
            return self.home.execute({
                "device": "humidifier",
                "action": "off"
            })

        elif name == "set_target_humidity":
            return self.home.execute({
                "device": "humidifier",
                "action": "set_humidity",
                "value": args["humidity"]
            })

        elif name == "turn_on_air_purifier":
            return self.home.execute({
                "device": "air_purifier",
                "action": "on"
            })

        elif name == "turn_off_air_purifier":
            return self.home.execute({
                "device": "air_purifier",
                "action": "off"
            })

        raise ValueError(f"Unknown tool: {name}")

    def execute_all(self, tool_calls):
        return [self.execute(call) for call in tool_calls]
