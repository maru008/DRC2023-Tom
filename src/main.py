# main.py
import sys

from utils.config_reader import read_config

from modules.speech_generation import SpeechGeneration
from modules.voice_recognition import VoiceRecognition
from modules.expression_generation import ExpressionGeneration
from modules.motion_generation import MotionGeneration

from database.mongo_tools import get_db, create_document, read_document, update_document, delete_document

##引数情報を取得
config = read_config()
IP = config.get("Server_Info","Server_ip")

user_input_val = sys.argv[1] if len(sys.argv) > 1 else 'n'
print("="*100)
if user_input_val == "y":
    DIALOG_MODE = "console_dialog"
    
    print("コンソール対話モード")
elif user_input_val == "n":
    DIALOG_MODE = "robot_dialog"
    print("ロボット対話モード")
print("="*100)

speech_gen = SpeechGeneration(DIALOG_MODE,IP,config.get("Server_Info","SpeechGenerator_port"))
voice_recog = VoiceRecognition(DIALOG_MODE,IP,config.get("Server_Info","SpeechRecognition_port"))
# expression_gen = ExpressionGeneration(DIALOG_MODE,IP,)
# motion_gen = MotionGeneration(DIALOG_MODE,IP,)

while True:
    input_text = voice_recog.recognize()

    if input_text in ["終了","quit"]:
        break
    
    speech_gen.speech_generate(input_text)
    
    

# db = get_db('my_database')
# collection = db['my_collection']

# # Create
# new_data = {'name': 'Alice', 'age': 25}
# id = create_document(collection, new_data)
# print(f"Inserted data with id {id}")

# # Read
# query = {'name': 'Alice'}
# result = read_document(collection, query)
# print(f"Read data: {result}")

# # Update
# new_data = {'age': 26}
# update_count = update_document(collection, query, new_data)
# print(f"Updated {update_count} documents")

# # Delete
# delete_count = delete_document(collection, query)
# print(f"Deleted {delete_count} documents")
