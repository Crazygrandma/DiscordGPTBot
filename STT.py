import whisper
class STTManager():
    def __init__(self,name) -> None:
        self.name = name
        self.model = whisper.load_model(name)