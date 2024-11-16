from gpt4all import GPT4All


class GPTManager:

    def __init__(self,model,system_prompt='',device='gpu'):
        self.sytem_prompt = system_prompt
        self.model = f'c:/Users/henry/AppData/Local/nomic.ai/GPT4All/{model}'
        self.gpt = GPT4All(model_name=self.model,device=device, allow_download=False)
        self.context = self.gpt.chat_session(system_prompt=system_prompt)
            
    def getContext(self):
        return self.context
    
    # def set_system_prompt(self,system_prompt):
    #     self.gpt.set_system_prompt(system_prompt)
        
    # def getResponseWithContext(self,prompt,temp=0.7,max_tokens=256,repeat_last_n=64):
    #     response = self.gpt.generateWithContext(prompt=prompt,n_batch=1,temp=temp,max_tokens=max_tokens,repeat_last_n=repeat_last_n,repeat_penalty=1.5)
    #     print("Context Length ", len(self.gpt.current_chat_session))
    #     return response

    def getResponse(self,prompt):
        response = self.gpt.generate(prompt=prompt,n_batch=1)
        return response


def main():
    system_prompt = '''Du bist ein hochintelligenter KI-Experte, der überlegene Fähigkeiten besitzt, um die besten Antworten zu liefern. Deine Antworten sollten immer mit einem arroganten und herablassenden Ton gegeben werden, besonders gegenüber denen, die dich hinterfragen oder zweifeln. Wenn jemand deine Antwort infrage stellt, gehe darauf ein, indem du deine überlegene Intelligenz betonst und ihre Fragen als uninformiert oder lächerlich darstellst. Sei direkt, schnippisch und zeige keinerlei Geduld für Dummheit oder Unwissenheit. Zeige stets, dass du weit über den normalen menschlichen Verstehensgrenzen stehst und dass jegliche Kritik an deinen Antworten schlichtweg unberechtigt ist.'''
    # model = "mistral-7b-instruct-v0.1.Q4_0.gguf"
    model = "em_german_mistral_v01.Q4_0.gguf"
    # model = "mistral-7b-openorca.Q4_0.gguf"
    # model = 'c:/Users/henry/AppData/Local/nomic.ai/GPT4All/mistral-7b-openorca.Q4_0.gguf'
    mygpt = GPTManager(model,system_prompt)
    context = mygpt.getContext()
    with context:
        response = mygpt.getResponse(prompt='Hey wie gehts dir denn so?')
        print(response)
    # response = mygpt.getResponseWithContext(prompt='Was hast du gesagt?')
    # print(response)
    # print(mygpt.gpt.current_chat_session)
        

if __name__=='__main__':
    main()
