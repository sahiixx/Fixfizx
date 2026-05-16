import sys
sys.path.insert(0, "/home/sahiix/Fixfizx/backend")
import emergentintegrations.llm.chat
print("Module:", emergentintegrations.llm.chat)
print("File:", getattr(emergentintegrations.llm.chat, '__file__', 'NO FILE'))
print("Attrs:", [a for a in dir(emergentintegrations.llm.chat) if not a.startswith('_')])
