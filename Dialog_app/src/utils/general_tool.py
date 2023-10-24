import datetime

def SectionPrint(text):
    print("="*100)
    print(text)
    print("="*100)
    
def elapsed_time(start_time):
    current_time = datetime.datetime.now()
    elapsed_time_ms = int((current_time - start_time).total_seconds() * 1000)
    return elapsed_time_ms