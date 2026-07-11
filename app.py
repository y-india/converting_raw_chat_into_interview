import streamlit as st

from converter import convert_chat as convert_linkedin
from converter_whatsapp import convert_chat as convert_whatsapp

# ----------------------------------------
# Page Config
# ----------------------------------------

st.set_page_config(
    page_title="Chat Converter",
    page_icon="💬",
    layout="centered"
)

# ----------------------------------------
# UI
# ----------------------------------------

st.title("💬 Chat Converter")

st.write(
    "Upload a LinkedIn or WhatsApp chat export (.txt), convert it into a structured conversation, and download the result."
)

chat_type = st.radio(
    "Select Chat Type",
    [
        "LinkedIn",
        "WhatsApp"
    ],
    horizontal=True
)

uploaded_file = st.file_uploader(
    f"Upload {chat_type} Chat",
    type=["txt"]
)

# ----------------------------------------
# Convert
# ----------------------------------------

if uploaded_file is not None:

    st.success(f"Loaded: {uploaded_file.name}")

    if st.button("🚀 Convert Chat", use_container_width=True):

        raw_chat = uploaded_file.read().decode("utf-8")

        with st.spinner(f"Converting {chat_type} chat..."):

            try:

                if chat_type == "LinkedIn":
                    output_text, output_filename = convert_linkedin(raw_chat)
                else:
                    output_text, output_filename = convert_whatsapp(raw_chat)

                st.success("Conversion completed!")

                st.download_button(
                    label="📥 Download Structured Chat",
                    data=output_text,
                    file_name=output_filename,
                    mime="text/plain",
                    use_container_width=True,
                )

            except Exception as e:

                st.error("Conversion failed.")
                st.exception(e)