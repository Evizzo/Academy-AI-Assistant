import json, uuid, os
from consts import CONVERSATION_FILE, INTRO_MESSAGE

def loadConversations():
    if not os.path.exists(CONVERSATION_FILE):
        data = {"chats": []}
        saveConversations(data)
        return data
    try:
        with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {"chats": []}
        saveConversations(data)
        return data
    if not isinstance(data, dict) or "chats" not in data:
        data = {"chats": []}
        saveConversations(data)
    return data

def saveConversations(data):
    with open(CONVERSATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def createNewChat(chatName="Novi Chat", client_id=None):
    data = loadConversations()
    chat = {
        "id": str(uuid.uuid4()),
        "client_id": client_id,
        "chatName": chatName,
        "messages": []
    }
    data["chats"].append(chat)
    saveConversations(data)
    first_message = INTRO_MESSAGE
    createMessage(chat["id"], first_message, "Bot")
    return chat

def getConversationsForClient(client_id):
    data = loadConversations()
    return [chat for chat in data["chats"] if chat.get("client_id") == client_id]

def getChat(chat_id, client_id=None):
    data = loadConversations()
    for chat in data["chats"]:
        if chat["id"] == chat_id:
            if client_id is None or chat.get("client_id") == client_id:
                return chat
    return None

def createMessage(chat_id, content, sender):
    data = loadConversations()
    for chat in data["chats"]:
        if chat["id"] == chat_id:
            message = {
                "id": str(uuid.uuid4()),
                "sender": sender,
                "content": content
            }
            if not chat.get("chatName") and content:
                chat["chatName"] = content[:50]
            chat["messages"].append(message)
            saveConversations(data)
            return message
    return None

def deleteChat(chat_id, client_id=None):
    data = loadConversations()
    data["chats"] = [chat for chat in data["chats"] if chat["id"] != chat_id or (client_id and chat.get("client_id") != client_id)]
    saveConversations(data)

def updateMessage(chat_id, messageId, newContent):
    data = loadConversations()
    for chat in data["chats"]:
        if chat["id"] == chat_id:
            for msg in chat["messages"]:
                if msg["id"] == messageId:
                    msg["content"] = newContent
                    break
            break
    saveConversations(data)

def deleteMessage(chat_id, messageId):
    data = loadConversations()
    for chat in data["chats"]:
        if chat["id"] == chat_id:
            chat["messages"] = [msg for msg in chat["messages"] if msg["id"] != messageId]
            break
    saveConversations(data)

def getLastMessages(chat_id, n=5):
    chat = getChat(chat_id)
    if chat:
        return chat["messages"][-n:]
    return []
