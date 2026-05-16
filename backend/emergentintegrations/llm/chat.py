"""
Mock emergentintegrations.llm.chat module.
"""

class UserMessage:
    def __init__(self, role: str = "user", content: str = ""):
        self.role = role
        self.content = content

class LlmChat:
    def __init__(self, model: str = "gpt-4", api_key: str = None, system_message: str = None):
        self.model = model
        self.api_key = api_key or "mock-key"
        self.system_message = system_message or "You are a helpful assistant."
        self.messages = []
        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def add_message(self, message: UserMessage):
        self.messages.append({"role": message.role, "content": message.content})

    async def send_message(self, message: UserMessage):
        self.add_message(message)
        return f"[MOCK] Response to: {message.content[:50]}..."

    def get_history(self):
        return self.messages.copy()

    def clear_history(self):
        self.messages.clear()
        if self.system_message:
            self.messages.append({"role": "system", "content": self.system_message})
