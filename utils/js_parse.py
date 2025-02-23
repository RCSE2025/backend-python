import json
from typing import Dict, List


def load_agents(file_name: str = "regions.json") -> List[Dict[str, str]]:
    with open(file_name, "r") as file:
        return json.load(file)


if __name__ == "__main__":
    print(load_agents("../regions.json"))
