
def SectionPrint(text):
    print("="*100)
    print(text)
    print("="*100)
    
def Create_dialog_log(user_input_text_ls:list,system_output_text_ls:list) -> str:
    output_text = ""
    for user_i, system_i in zip(user_input_text_ls,system_output_text_ls):
        output_text += "system> " + system_i + "\n"
        output_text += "user> " + user_i + "\n"
    return output_text