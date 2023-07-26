import openai

class NLG:
    def __init__(self,config):
        self.OpenAI_key = config.get("API_Key","OpenAI")
        openai.api_key = self.OpenAI_key
        
        
    def completion(self,model,new_message_text:str, settings_text:str = '', past_messages:list = []):
        """
        この関数は、新しいメッセージテキスト、オプションの設定テキスト、過去のメッセージのリストを入力として受け取り、OpenAIのGPT-3モデルを使用して応答メッセージを生成する関数です。

        引数:
        - new_message_text (str)：モデルが応答メッセージを生成するために使用する新しいメッセージテキスト。
        - settings_text (str、オプション)：過去のメッセージリストにシステムメッセージとして追加されるオプションの設定テキスト。デフォルトは '' です。
        - past_messages (list、オプション)：モデルが応答メッセージを生成するために使用するオプションの過去のメッセージのリスト。デフォルトは [] です。

        戻り値:
        - tuple : 応答メッセージテキストと、新しいメッセージと応答メッセージを追加した更新された過去のメッセージのリストを含むタプルを返します。
        """
        
        if len(past_messages) == 0 and len(settings_text) != 0:
            system = {"role": "system", "content": settings_text}
            past_messages.append(system)
        new_message = {"role": "user", "content": new_message_text}
        past_messages.append(new_message)

        result = openai.ChatCompletion.create(
            # model="gpt-3.5-turbo",
            model=model,
            messages=past_messages
        )
        response_message = {"role": "assistant", "content": result.choices[0].message.content}
        past_messages.append(response_message)
        response_message_text = result.choices[0].message.content
        return response_message_text, past_messages
    
    def ChatGPT(self,new_message_text,settings_text,past_messages):
        response_message_text, past_messages = self.completion("gpt-3.5-turbo",new_message_text,settings_text,past_messages)
        return response_message_text