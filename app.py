import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="Hộ kinh doanh | Trợ lý pháp luật",
    page_icon="⚖️",
    layout="wide",
)

st.markdown("""
<style>
    :root { --ink: #1d2a2a; --muted: #667474; --paper: #f7f4ed; --accent: #b45b35; }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stSidebar"] { background: #203b3a; }
    [data-testid="stSidebar"] * { color: #f7f4ed; }
    .hero { padding: 1.5rem 0 1rem; border-bottom: 1px solid #d8d2c6; margin-bottom: 1.5rem; }
    .eyebrow { color: var(--accent); font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: .75rem; }
    .hero h1 { font-size: 2.4rem; line-height: 1.05; margin: .35rem 0; color: var(--ink); }
    .hero p { color: var(--muted); max-width: 680px; font-size: 1rem; }
    .source-card { border-left: 3px solid var(--accent); background: #fffdf8; padding: .8rem 1rem; margin: .5rem 0; }
    .source-meta { color: var(--muted); font-size: .82rem; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_source(source: dict) -> None:
    metadata = source.get("metadata", {})
    url = metadata.get("url")
    link_html = (
        f"<div class='source-meta'><a href='{url}' target='_blank'>{url}</a></div>"
        if url else ""
    )
    st.markdown(
        f"<div class='source-card'><strong>{metadata.get('title', 'Tài liệu')}</strong>"
        f"<div class='source-meta'>{metadata.get('source', '')} · score {source.get('score', 0):.3f}</div>"
        f"{link_html}</div>",
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.markdown("## ⚖️ Hộ kinh doanh")
    st.caption("Trợ lý tra cứu từ bộ tài liệu pháp luật và thuế đã thu thập.")
    top_k = st.slider("Số chunks", 3, 10, 5)
    st.divider()
    st.caption("Nguồn trả lời được hiển thị bên dưới mỗi phản hồi. Nội dung không thay thế tư vấn pháp lý.")

st.markdown("""
<section class="hero">
    <div class="eyebrow">Pháp luật cho hộ kinh doanh</div>
    <h1>Tra cứu rõ ràng, có nguồn.</h1>
    <p>Đặt câu hỏi về đăng ký kinh doanh, thuế, hóa đơn hoặc thương mại điện tử. Câu trả lời chỉ dựa trên tài liệu trong kho dữ liệu của nhóm.</p>
</section>
""", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"Nguồn tham khảo · {message.get('retrieval_source', 'hybrid')}"):
                for source in message["sources"]:
                    render_source(source)

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu tài liệu..."):
            result = generate_with_citation(query, top_k=top_k)
        answer = result["answer"]
        sources = result.get("sources", [])
        retrieval_source = result.get("retrieval_source", "none")
        st.markdown(answer)
        if sources:
            with st.expander(f"Nguồn tham khảo · {retrieval_source}"):
                for source in sources:
                    render_source(source)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
