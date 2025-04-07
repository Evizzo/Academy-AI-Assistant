import tiktoken

from logger import logger


def numTokens(text, model="gpt-3.5-turbo"):
    logger.warning("Input token limit nadmasen!")
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
