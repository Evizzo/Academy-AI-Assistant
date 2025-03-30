import json, uuid, os
from consts import CONVERSATION_FILE

def loadConversation():
    if not os.path.exists(CONVERSATION_FILE):
        data = {"chatName": "", "messages": []}
        saveConversation(data)
    else:
        try:
            with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {"chatName": "", "messages": []}
            saveConversation(data)
    return data

def saveConversation(data):
    with open(CONVERSATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def createMessage(content, sender):
    data = loadConversation()
    message = {
        "id": str(uuid.uuid4()),
        "sender": sender,
        "content": content
    }
    if not data.get("chatName"):
        data["chatName"] = content[:50]
    data["messages"].append(message)
    saveConversation(data)
    return message

def updateMessage(messageId, newContent):
    data = loadConversation()
    for msg in data["messages"]:
        if msg["id"] == messageId:
            msg["content"] = newContent
            break
    saveConversation(data)

def deleteMessage(messageId):
    data = loadConversation()
    data["messages"] = [msg for msg in data["messages"] if msg["id"] != messageId]
    saveConversation(data)

def getLastMessages(n=5):
    data = loadConversation()
    return data["messages"][-n:]
