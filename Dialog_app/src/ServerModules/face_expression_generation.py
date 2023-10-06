import sys

from .base import Base

class ExpressionGeneration(Base):
    def __init__(self, DIALOG_MODE, ip, port):
        super().__init__(ip, int(port))
        
        self.DIALOG_MODE = DIALOG_MODE
        
        self.preset_expressions = ["fullsmile", "bad", "angry", "eye-close", "eye-open", "eye-fullopen", "eye-up", "eye-down", "eye-open_lower", "smile_sales"]
        self.default_expression = "fullsmile"
            
    def set_expression(self, face_ex_signal):
        if self.DIALOG_MODE == "console_dialog":
            return None
        else:
            print(f"face expression:{face_ex_signal}")
            command = "expression " + face_ex_signal
            self._send_command(command)
            return command

    def reset_expression(self):
        return self.set_expression(self.default_expression)
    
#表情一覧
#"fullsmile", "bad", "angry", "eye-close", "eye-open", "eye-fullopen", "eye-up", "eye-down", "eye-open_lower", "smile_sales"
