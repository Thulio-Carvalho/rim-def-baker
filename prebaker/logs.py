# prebaker/logs.py

class DeepProfiler:
    @staticmethod
    def Start(msg):
        pass  # Placeholder for actual profiling/timing

    @staticmethod
    def End():
        pass

def Log_Error(msg):
    print(f"[ERROR] {msg}")

def Log_Warning(msg):
    print(f"[WARN] {msg}")

def Log_Message(msg):
    print(f"[LOG] {msg}")

