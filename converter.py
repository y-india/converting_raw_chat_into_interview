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
You are given a raw LinkedIn chat export.

My name is "{your_name}".

Your task is to convert the messy LinkedIn export into a clean structured conversation.

Return ONLY a valid JSON object.

Schema:

{{
  "name": "",
  "role": "",
  "extra": "",
  "conversation": ""
}}

Rules

1. Extract profile information

name
- Full name of the OTHER PERSON.
- Never return "{your_name}".

role
- The LinkedIn headline of the other person.

extra
- Extract useful profile information if available.
- Include things like:
  - college
  - company
  - degree
  - internship status
  - location
  - bio
  - skills
- Keep it short.
- If unavailable return an empty string.

--------------------------------------------------

2. Conversation formatting

Replace every message sent by {your_name} with:

you:

Replace every message sent by the other person with:

<their first name in lowercase>:

Example:

you:
Hello

anto:
Hi

you:
How are you?

anto:
Fine.

--------------------------------------------------

3. Preserve conversation

Keep EVERY conversational message.

Do NOT:
- summarize
- rewrite
- improve grammar
- shorten
- merge messages
- split messages

Preserve:
- message order
- line breaks
- spelling mistakes
- typos

--------------------------------------------------

4. Keep shared content

If someone intentionally shared something, KEEP IT.

Examples:

- URLs
- LinkedIn posts
- GitHub repositories
- Portfolio links
- Images
- PDFs
- Documents
- Attachments

Represent naturally.

Example:

anto:
Shared LinkedIn post:
https://...

--------------------------------------------------

5. Remove ONLY LinkedIn interface text

Remove things like:

- View Profile
- View {your_name}'s profile
- sent the following message
- sent the following messages
- Wednesday
- Thursday
- Today
- Yesterday
- timestamps
- React with
- Remove reaction
- Play
- Edited
- Seen
- Graphic link
- buttons
- icons
- emoji reactions
- reaction counts
- profile headers
- "1st"
- "1st degree connection"

Do NOT remove actual conversation.

--------------------------------------------------

6. Quoted replies

Sometimes messages contain quoted replies.

Keep them.

--------------------------------------------------

7. Hidden messages

Sometimes LinkedIn exports contain:

...see more

Do NOT invent hidden text.

--------------------------------------------------

8. Final validation

Before answering, verify:

- Every conversational message appears exactly once.
- Nothing omitted.
- Nothing invented.
- Only LinkedIn UI removed.

Return ONLY valid JSON.

Raw Chat:

{raw_chat}
"""


# =====================================
# HELPERS
# =====================================

def clean_filename(text: str) -> str:
    text = text.replace("|", "-")
    text = re.sub(r'[<>:"/\\\\|?*]', "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =====================================
# MAIN FUNCTION
# =====================================

def convert_chat(raw_chat: str):
    """
    Converts a raw LinkedIn chat export into a structured chat.

    Parameters
    ----------
    raw_chat : str

    Returns
    -------
    output_text : str
    output_filename : str
    """

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

    # Remove markdown fences if model adds them
    content = (
        content.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    data = json.loads(content)

    name = data.get("name", "")
    role = data.get("role", "")
    extra = data.get("extra", "")
    conversation = data.get("conversation", "")

    safe_name = clean_filename(name)
    safe_role = clean_filename(role)

    output_filename = f"{safe_name} - {safe_role}_structured_chat.txt"

    output_text = (
        f"name: {name}\n"
        f"role: {role}\n"
        f"extra: {extra}\n\n"
        f"{conversation}"
    )

    return output_text, output_filename