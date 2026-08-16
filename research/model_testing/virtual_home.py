def automation(home, room):
    env = home.devices["environment"]
    humidity = env["humidity"][room]
    aqi = env["air_quality"][room]
    lux = env["illumination"][room]

    if humidity < 50:
        return {
            "device": "humidifier",
            "action": "on"
        }

    if aqi > 100:
        return {
            "device": "air_purifier",
            "action": "on"
        }

    if lux < 100:
        return {
            "device": "light",
            "action": "on",
            "room": room
        }

    return None


class SmartHome:

    def __init__(self):

        self.devices = {
            "light": {
                "living_room": {
                    "state": "off",
                    "brightness": 50
                }
            },

            "thermostat": {
                "temperature": 21
            },

            "environment": {

                "temperature": {
                    "living_room": 21,
                    "bedroom": 20
                },

                "humidity": {
                    "living_room": 40,
                    "bedroom": 55
                },

                "air_quality": {
                    "living_room": 45,
                    "bedroom": 80
                },

                "illumination": {
                    "living_room": 300,
                    "bedroom": 150
                }
            },

            "air_purifier": {
                "state": "off"
            },

            "humidifier": {
                "state": "off",
                "target_humidity": 45
            }
        }

    def execute(self, command):

        device = command["device"]

        if device == "light":

            room = command["room"]

            if command["action"] == "on":
                self.devices["light"][room]["state"] = "on"

            elif command["action"] == "off":
                self.devices["light"][room]["state"] = "off"

            elif command["action"] == "brightness":
                self.devices["light"][room]["brightness"] = command["value"]

        elif device == "thermostat":
            if command["action"] == "set":
                self.devices["thermostat"]["temperature"] = command["value"]

        elif device == "air_purifier":
            self.devices["air_purifier"]["state"] = command["action"]

        elif device == "humidifier":

            if command["action"] in ("on", "off"):
                self.devices["humidifier"]["state"] = command["action"]

            elif command["action"] == "set_humidity":
                self.devices["humidifier"]["target_humidity"] = command["value"]

        return self.devices

    def load_state(self, state, room="living_room"):

        env = self.devices["environment"]

        if "temperature" in state:
            env["temperature"][room] = state["temperature"]

        if "humidity" in state:
            env["humidity"][room] = state["humidity"]

        if "air_quality" in state:
            env["air_quality"][room] = state["air_quality"]

        if "illumination" in state:
            env["illumination"][room] = state["illumination"]

        if "light_state" in state:
            self.devices["light"][room]["state"] = state["light_state"]

        if "brightness" in state:
            self.devices["light"][room]["brightness"] = state["brightness"]
    def tick(self):

        env = self.devices["environment"]

        temp = self.devices["thermostat"]["temperature"]

        current = env["temperature"]["living_room"]

        if current < temp:
            env["temperature"]["living_room"] += 0.2
        elif current > temp:
            env["temperature"]["living_room"] -= 0.2

        humidity = env["humidity"]["living_room"]

        if self.devices["humidifier"]["state"] == "on":
            humidity += 1.5
        else:
            humidity -= 0.2

        humidity = max(20, min(80, humidity))

        env["humidity"]["living_room"] = humidity

        aqi = env["air_quality"]["living_room"]

        if self.devices["air_purifier"]["state"] == "on":
            aqi -= 3
        else:
            aqi += 0.5

        aqi = max(0, min(500, aqi))

        env["air_quality"]["living_room"] = aqi

        light = self.devices["light"]["living_room"]

        if light["state"] == "on":

            env["illumination"]["living_room"] = (
                    100 + light["brightness"] * 8
            )

        else:
            env["illumination"]["living_room"] = 30

    def execute_all(self, commands):

        for command in commands:
            self.execute(command)

    def reset(self):
        self.__init__()

    def get_state(self):
        return self.devices
