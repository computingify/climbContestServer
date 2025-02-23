class Handler:
    def __init__(self, config):
        self.config = config

    def handle(self, data):
        print(f"Handling data: {data}")
        return data