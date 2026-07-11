from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

# =====================================
# CONFIG
# =====================================

YOUR_NAME = "Yuvraj"

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =====================================
# PROMPT
# =====================================

PROMPT_TEMPLATE = """
Convert the following exported WhatsApp chat into JSON.

My name is "{your_name}".

Return ONLY valid JSON:

{
  "name": "",
  "extra": "",
  "conversation": ""
}

Rules:

- "name" = the other person's full name (never "{your_name}").
- "extra" = short facts learned from the chat (role, company, college, skills, location, etc.). If none, use "".
- "conversation" = preserve the conversation exactly.

Conversation format:

you:
<all messages from {your_name}>

<first_name_lowercase>:
<all messages from the other person>

Requirements:

- Keep every conversational message exactly once.
- Preserve wording, spelling, emojis, line breaks, URLs, and media placeholders.
- Do not summarize, rewrite, merge, split, or invent messages.
- Remove only WhatsApp metadata such as timestamps, dates, encryption notice, edited labels, deleted-message notifications, and other system messages.
- Ignore empty messages.

Raw chat:

{raw_chat}
"""

# =====================================
# HELPERS
# =====================================

def clean_filename(text: str):
    text = text.replace("|", "-")
    text = re.sub(r'[<>:"/\\\\|?*]', "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =====================================
# MAIN
# =====================================

def convert_chat(raw_chat):

    prompt = PROMPT_TEMPLATE.format(
        raw_chat=raw_chat,
        your_name=YOUR_NAME
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content.strip()

    content = (
        content.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    data = json.loads(content)

    name = data.get("name", "")
    extra = data.get("extra", "")
    conversation = data.get("conversation", "")

    # Conversion log

    LOG_FILE = "chat_converted_of.txt"

    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w", encoding="utf-8").close()

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        converted = {line.strip() for line in f if line.strip()}

    if name and name not in converted:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(name + "\n")

    safe_name = clean_filename(name)

    filename = f"{safe_name}_whatsapp_chat.txt"

    output = (
        f"name: {name}\n"
        f"extra: {extra}\n\n"
        f"{conversation}"
    )

    return output, filename