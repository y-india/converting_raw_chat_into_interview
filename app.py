import streamlit as st
from converter import convert_chat

# ----------------------------------------
# Page Config
# ----------------------------------------

st.set_page_config(
    page_title="LinkedIn Chat Converter",
    page_icon="💬",
    layout="centered"
)

# ----------------------------------------
# UI
# ----------------------------------------

st.title("💬 LinkedIn Chat Converter")
st.write(
    "Upload a LinkedIn chat export (.txt), convert it into a structured chat, and download the result."
)

uploaded_file = st.file_uploader(
    "Upload LinkedIn Chat",
    type=["txt"]
)

# ----------------------------------------
# Convert
# ----------------------------------------

if uploaded_file is not None:

    st.success(f"Loaded: {uploaded_file.name}")

    if st.button("🚀 Convert Chat", use_container_width=True):

        raw_chat = uploaded_file.read().decode("utf-8")

        with st.spinner("Converting..."):

            try:
                output_text, output_filename = convert_chat(raw_chat)

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
                