import uuid
import json
from db import getDbConnection
from consts import INTRO_MESSAGE

def createNewChat(chatName="Novi Chat", client_id=None):
    chat_id = str(uuid.uuid4())
    empty_messages = json.dumps([])
    connection = getDbConnection()
    cursor = connection.cursor()
    query = "INSERT INTO conversations (id, client_id, chatName, messages) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (chat_id, client_id, chatName, empty_messages))
    connection.commit()
    cursor.close()
    connection.close()
    first_message = INTRO_MESSAGE
    createMessage(chat_id, first_message, "Bot")
    return {"id": chat_id, "client_id": client_id, "chatName": chatName, "messages": []}

def getConversationsForClient(client_id):
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM conversations WHERE client_id = %s"
    cursor.execute(query, (client_id,))
    rows = cursor.fetchall()
    for row in rows:
        row["messages"] = json.loads(row["messages"])
    cursor.close()
    connection.close()
    return list(reversed(rows))

def getChat(chat_id, client_id=None):
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)
    if client_id is not None:
        query = "SELECT * FROM conversations WHERE id = %s AND client_id = %s"
        cursor.execute(query, (chat_id, client_id))
    else:
        query = "SELECT * FROM conversations WHERE id = %s"
        cursor.execute(query, (chat_id,))
    row = cursor.fetchone()
    if row:
        row["messages"] = json.loads(row["messages"])
    cursor.close()
    connection.close()
    return row

def createMessage(chat_id, content, sender):
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT messages, chatName FROM conversations WHERE id = %s"
    cursor.execute(query, (chat_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        connection.close()
        return None

    messages = json.loads(result["messages"])
    chatName = result["chatName"]

    message = {
        "id": str(uuid.uuid4()),
        "sender": sender,
        "content": content
    }
    if sender == "User" and not any(msg["sender"] == "User" for msg in messages):
        new_chatName = content[:50] + ("..." if len(content) > 50 else "")
    else:
        new_chatName = chatName

    messages.append(message)
    messages_json = json.dumps(messages)

    update_query = "UPDATE conversations SET messages = %s, chatName = %s WHERE id = %s"
    cursor.execute(update_query, (messages_json, new_chatName, chat_id))
    connection.commit()
    cursor.close()
    connection.close()
    return message

def deleteChat(chat_id, client_id=None):
    connection = getDbConnection()
    cursor = connection.cursor()
    if client_id is not None:
        query = "DELETE FROM conversations WHERE id = %s AND client_id = %s"
        cursor.execute(query, (chat_id, client_id))
    else:
        query = "DELETE FROM conversations WHERE id = %s"
        cursor.execute(query, (chat_id,))
    connection.commit()
    cursor.close()
    connection.close()

def updateMessage(chat_id, messageId, newContent):
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT messages FROM conversations WHERE id = %s"
    cursor.execute(query, (chat_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        connection.close()
        return

    messages = json.loads(result["messages"])
    for msg in messages:
        if msg["id"] == messageId:
            msg["content"] = newContent
            break
    messages_json = json.dumps(messages)
    update_query = "UPDATE conversations SET messages = %s WHERE id = %s"
    cursor.execute(update_query, (messages_json, chat_id))
    connection.commit()
    cursor.close()
    connection.close()

def deleteMessage(chat_id, messageId):
    connection = getDbConnection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT messages FROM conversations WHERE id = %s"
    cursor.execute(query, (chat_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        connection.close()
        return

    messages = json.loads(result["messages"])
    messages = [msg for msg in messages if msg["id"] != messageId]
    messages_json = json.dumps(messages)
    update_query = "UPDATE conversations SET messages = %s WHERE id = %s"
    cursor.execute(update_query, (messages_json, chat_id))
    connection.commit()
    cursor.close()
    connection.close()

def getLastMessages(chat_id, n=5):
    chat = getChat(chat_id)
    if chat:
        return chat["messages"][-n:]
    return []
