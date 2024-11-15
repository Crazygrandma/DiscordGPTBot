import whisper

class STTManager():

    def __init__(self,name) -> None:
        self.name = name
        self.model = whisper.load_model(name)
        
        
def main():
    print(whisper.available_models())      

if __name__ == '__main__':
    main()