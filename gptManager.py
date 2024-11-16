from gpt4all import GPT4All


class GPTManager:

    def __init__(self,model,system_prompt='',device='gpu'):
        self.sytem_prompt = system_prompt
        self.model = f'c:/Users/henry/AppData/Local/nomic.ai/GPT4All/{model}'
        self.gpt = GPT4All(model_name=self.model,device=device, allow_download=False)
        self.context = self.gpt.chat_session(system_prompt=system_prompt)
            
    def getContext(self):
        return self.context

    def getResponse(self,prompt,max_tokens=128,repeat_penalty=1.6,temp=0.9):
        response = self.gpt.generate(prompt=prompt,n_batch=1,max_tokens=128,repeat_penalty=1.6,temp=0.9,repeat_last_n=1)
        return response


def main():
    system_prompt = ''''''
    # model = "mistral-7b-instruct-v0.1.Q4_0.gguf"
    # model = "em_german_mistral_v01.Q4_0.gguf"
    model = "em_german_leo_mistral.Q4_0.gguf"
    # model = "em_german_7b_v01.Q4_K_M.gguf"
    # model = "mistral-7b-openorca.Q4_0.gguf"
    # model = 'c:/Users/henry/AppData/Local/nomic.ai/GPT4All/mistral-7b-openorca.Q4_0.gguf'
    mygpt = GPTManager(model,system_prompt)
    # context = mygpt.getContext()
    # with context:
    #     response = mygpt.getResponse(prompt='Hey what is the capital of Berlin?',repeat_penalty=1.2,temp=0.5,max_tokens=128)
    #     print(response)
    
    # response = mygpt.getResponse("Hey wie gehts dir?")
    # print(response)
    # response = mygpt.getResponseWithContext(prompt='Was hast du gesagt?')
    # print(response)
    # print(mygpt.gpt.current_chat_session)
        

if __name__=='__main__':
    main()
