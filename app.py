import json
import urllib.error
import urllib.request

import streamlit as st
from retrieval import search_books, passages, index


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Transformer AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"


# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700;800&display=swap');

/* ---------- Design tokens ---------- */
:root {
    --background: #070d1a;
    --surface: #0f1a2e;
    --surface-light: #15233b;
    --border: #22344f;
    --blue: #6aa8ff;
    --blue-deep: #2f6bef;
    --gold: #e3b866;
    --gold-soft: #f0d49b;
    --text: #eef3fb;
    --muted: #9fb0c9;
    --serif: 'Fraunces', Georgia, 'Times New Roman', serif;
    --sans: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

/* ---------- Page ---------- */
.stApp {
    background:
        radial-gradient(ellipse at 12% 0%, rgba(34, 78, 140, 0.55) 0%, transparent 42%),
        radial-gradient(ellipse at 95% 8%, rgba(227, 184, 102, 0.07) 0%, transparent 35%),
        linear-gradient(160deg, #070d1a, #0a1424 55%, #0e192d);
    color: var(--text);
    font-family: var(--sans);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1450px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
}

::selection {
    background: rgba(227, 184, 102, 0.35);
    color: #ffffff;
}

::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: #243a5a;
    border-radius: 10px;
    border: 2px solid #0a1425;
}
::-webkit-scrollbar-thumb:hover {
    background: #34507c;
}

/* ---------- Typography ---------- */
h1, h2, h3 {
    color: var(--text) !important;
    font-family: var(--serif);
    font-weight: 600;
    letter-spacing: -0.01em;
}

p, label, .stCaption {
    color: var(--muted);
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #2a4163 20%, #2a4163 80%, transparent);
}

code {
    color: var(--gold-soft);
    background: rgba(106, 168, 255, 0.10);
    border-radius: 6px;
    padding: 0.1em 0.38em;
}
pre code {
    background: none;
    padding: 0;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08111f, #0a1628 60%, #0b1830);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

[data-testid="stSidebar"] h1 {
    font-size: 1.85rem;
    line-height: 1.15;
    padding-bottom: 0.1rem;
}

[data-testid="stSidebar"] h3 {
    font-size: 1.05rem;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
    color: var(--muted);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    width: 100%;
    padding: 10px 14px;
    margin-bottom: 3px;
    border-radius: 12px;
    border: 1px solid transparent;
    transition: background 0.2s ease, border-color 0.2s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(106, 168, 255, 0.08);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(106, 168, 255, 0.20), rgba(106, 168, 255, 0.04));
    border-color: rgba(106, 168, 255, 0.28);
    box-shadow: inset 3px 0 0 var(--gold);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    font-size: 15px;
    font-weight: 500;
}

/* ---------- Hero ---------- */
.hero {
    position: relative;
    overflow: hidden;
    padding: 46px 48px 50px 48px;
    padding-right: 390px;
    border-radius: 26px;
    border: 1px solid #2a4263;
    background:
        radial-gradient(ellipse at 88% 125%, rgba(227, 184, 102, 0.18), transparent 55%),
        radial-gradient(ellipse at 0% 0%, rgba(106, 168, 255, 0.20), transparent 52%),
        linear-gradient(120deg, #132a48, #0e1a2e 78%);
    box-shadow:
        0 34px 60px -34px rgba(0, 0, 0, 0.75),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
    margin-bottom: 28px;
    animation: heroIn 0.7s cubic-bezier(0.2, 0.7, 0.2, 1) both;
}

@keyframes heroIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 6px 14px;
    border-radius: 999px;
    border: 1px solid rgba(227, 184, 102, 0.38);
    background: rgba(227, 184, 102, 0.08);
    color: var(--gold-soft);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.hero-tag::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--gold);
    box-shadow: 0 0 10px var(--gold);
}

.hero-title {
    position: relative;
    color: #f4f8ff;
    font-family: var(--serif);
    font-size: 46px;
    font-weight: 600;
    line-height: 1.1;
    letter-spacing: -0.02em;
    margin-top: 20px;
    margin-bottom: 16px;
    max-width: 640px;
}

.hero-description {
    position: relative;
    color: #b9cae2;
    font-size: 16px;
    line-height: 1.75;
    max-width: 560px;
}

/* Bookshelf illustration (pure CSS, decorative) */
.hero-spines {
    position: absolute;
    right: 48px;
    bottom: 0;
    height: 200px;
    display: flex;
    align-items: flex-end;
    gap: 6px;
    padding: 0 14px;
    border-bottom: 4px solid #4a3b20;
    box-shadow: 0 6px 18px -4px rgba(227, 184, 102, 0.25);
    pointer-events: none;
}

.hero-spines span {
    position: relative;
    display: block;
    border-radius: 4px 4px 0 0;
    box-shadow: inset -4px 0 6px rgba(0, 0, 0, 0.28), inset 2px 0 3px rgba(255, 255, 255, 0.12);
}

.hero-spines span::before,
.hero-spines span::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    height: 3px;
    background: rgba(255, 255, 255, 0.32);
}
.hero-spines span::before { top: 16px; }
.hero-spines span::after  { bottom: 16px; }

.hero-spines span:nth-child(1) { width: 26px; height: 120px; background: #2f5fb8; }
.hero-spines span:nth-child(2) { width: 34px; height: 162px; background: #d8ab55; }
.hero-spines span:nth-child(3) { width: 24px; height: 136px; background: #1f3d6b; }
.hero-spines span:nth-child(4) { width: 38px; height: 178px; background: #5b8fe6; }
.hero-spines span:nth-child(5) { width: 27px; height: 108px; background: #b88a3e; }
.hero-spines span:nth-child(6) { width: 31px; height: 150px; background: #274a82; }
.hero-spines span:nth-child(7) {
    width: 25px;
    height: 142px;
    margin-left: 10px;
    background: #8fb8f5;
    transform: rotate(9deg);
    transform-origin: bottom left;
}

@media (max-width: 1100px) {
    .hero {
        padding: 34px 28px 38px 28px;
    }
    .hero-spines {
        display: none;
    }
    .hero-title {
        font-size: 34px;
    }
}

/* ---------- Feature cards ---------- */
.feature-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(160deg, #15263f, #0d182a);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
    min-height: 140px;
    margin-bottom: 10px;
    transition: border-color 0.25s ease;
}

.feature-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 64px;
    height: 2px;
    background: linear-gradient(90deg, var(--gold), transparent);
}

.feature-card:hover {
    border-color: #38577f;
}

.feature-icon {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 21px;
    margin-bottom: 14px;
    border-radius: 12px;
    background: rgba(106, 168, 255, 0.10);
    border: 1px solid rgba(106, 168, 255, 0.24);
}

.feature-title {
    color: #f4f8ff;
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 6px;
}

.feature-text {
    color: #a9bad3;
    font-size: 13px;
    line-height: 1.6;
}

/* ---------- Metrics ---------- */
div[data-testid="stMetric"] {
    position: relative;
    overflow: hidden;
    background: linear-gradient(150deg, #162945, #0f1c31);
    border: 1px solid var(--border);
    padding: 20px 22px;
    border-radius: 18px;
    box-shadow: 0 18px 34px -26px rgba(0, 0, 0, 0.9);
}

div[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    left: 0;
    top: 18px;
    bottom: 18px;
    width: 3px;
    border-radius: 0 3px 3px 0;
    background: linear-gradient(180deg, var(--gold), rgba(227, 184, 102, 0.1));
}

div[data-testid="stMetricLabel"] {
    color: #b6c9e2 !important;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
    color: #f2f7ff !important;
    font-family: var(--serif);
    font-weight: 600;
    letter-spacing: -0.01em;
}

/* ---------- Buttons ---------- */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(110deg, #2563eb, #3b82f6);
    color: white;
    border: 1px solid #60a5fa;
    border-radius: 12px;
    font-weight: 600;
    padding: 0.55rem 1rem;
    box-shadow: 0 10px 22px -14px rgba(59, 130, 246, 0.9);
    transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #1d4ed8;
    border-color: #93c5fd;
    color: white;
    transform: translateY(-1px);
}

.stButton > button:focus-visible,
.stFormSubmitButton > button:focus-visible {
    outline: 2px solid var(--gold);
    outline-offset: 2px;
}

/* ---------- Inputs ---------- */
.stTextInput input,
.stTextArea textarea,
[data-testid="stChatInput"] textarea {
    background: #0f1c32;
    color: #f1f7ff;
    border: 1px solid #344c6c;
    border-radius: 14px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--blue);
    box-shadow: 0 0 0 3px rgba(106, 168, 255, 0.18);
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder {
    color: #6f84a3;
}

[data-testid="stChatInput"] {
    border-radius: 16px;
}

[data-testid="stBottom"] > div {
    background: linear-gradient(180deg, rgba(10, 20, 37, 0), #0a1425 40%);
}

[data-testid="stForm"] {
    background: rgba(15, 27, 46, 0.65);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
}

/* ---------- Chat ---------- */
[data-testid="stChatMessage"] {
    background: rgba(15, 27, 46, 0.78);
    border: 1px solid #233853;
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 14px;
    box-shadow: 0 16px 32px -26px rgba(0, 0, 0, 0.9);
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(26, 44, 74, 0.62);
    border-color: #2b4468;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: #e3ecf8;
    font-size: 15.5px;
    line-height: 1.75;
}

[data-testid="stChatMessageAvatarUser"] {
    background: linear-gradient(135deg, #e3b866, #b88a3e);
    color: #1a1305;
}

[data-testid="stChatMessageAvatarAssistant"] {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    color: #ffffff;
}

/* ---------- Expanders (sources) ---------- */
[data-testid="stExpander"] {
    background: rgba(16, 29, 50, 0.85);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    padding: 12px 16px;
    font-weight: 600;
}

[data-testid="stExpander"] summary p {
    color: var(--text);
    font-weight: 600;
}

[data-testid="stExpander"] summary:hover {
    background: rgba(106, 168, 255, 0.07);
}

/* ---------- Alerts ---------- */
[data-testid="stAlert"] {
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

/* ---------- Chrome ---------- */
#MainMenu, footer {
    visibility: hidden;
}

@media (prefers-reduced-motion: reduce) {
    .hero {
        animation: none;
    }
    .stButton > button,
    .stFormSubmitButton > button,
    .feature-card,
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        transition: none;
    }
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_book_names():
    return sorted(set(
        p.get("book", "Unknown") for p in passages
    ))


def generate_answer(question, results):
    """Ask Ollama to answer using retrieved book passages."""

    context_parts = []

    for number, result in enumerate(results, start=1):
        context_parts.append(
            f"[Source {number}]\n"
            f"Book: {result.get('book', 'Unknown')}\n"
            f"Page: {result.get('page', 'Unknown')}\n"
            f"Passage: {result.get('text', '')}"
        )

    context = "\n\n".join(context_parts)

    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Transformer, a helpful book-grounded "
                    "learning assistant. Answer the user's question "
                    "in clear, natural language. Explain concepts "
                    "rather than copying whole passages. Use simple "
                    "examples when helpful. Base factual claims about "
                    "the books on the supplied context. Do not invent "
                    "book contents or citations. If the context does "
                    "not contain enough information, say so honestly. "
                    "Cite relevant sources in the answer using the "
                    "format [Book name, page X]. Distinguish your "
                    "explanation from anything directly stated by a book."
                )
            },
            {
                "role": "user",
                "content": (
                    f"QUESTION:\n{question}\n\n"
                    f"RETRIEVED BOOK CONTEXT:\n{context}\n\n"
                    "Answer the question helpfully using this context. "
                    "Include relevant book and page citations. If the "
                    "sources do not adequately answer the question, "
                    "explain the limitation instead of guessing."
                )
            }
        ],
        "options": {
            "temperature": 0.3
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=180) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data["message"]["content"].strip()


def answer_question(question):
    """Retrieve evidence, then generate a natural-language answer."""

    with st.spinner("Searching your books..."):
        results = search_books(question, limit=5)

    if not results:
        return (
            "I couldn't find relevant passages in your indexed books. "
            "Try rephrasing the question or searching for a related topic."
        ), []

    with st.spinner("Reading sources and preparing your answer..."):
        answer = generate_answer(question, results)

    return answer, results


def show_sources(results):
    if not results:
        return

    with st.expander(f"📚 View {len(results)} book sources"):
        for number, result in enumerate(results, start=1):
            book = result.get("book", "Unknown")
            page = result.get("page", "Unknown")

            st.markdown(f"**{number}. {book} — Page {page}**")
            st.caption(
                f"Search relevance: {result.get('score', 0):.3f}"
            )
            st.write(result.get("text", ""))
            if number < len(results):
                st.divider()


def show_search_results(question):
    with st.spinner("Searching your book collection..."):
        results = search_books(question, limit=5)

    if not results:
        st.warning("No matching passages found. Try different keywords.")
        return

    st.success(f"Found {len(results)} relevant passages.")
    show_sources(results)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("# 📚 Transformer")
    st.caption("YOUR PERSONAL KNOWLEDGE ASSISTANT")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "💬 Chat",
            "📖 Library",
            "🔎 Search",
            "⚙️ Settings",
            "ℹ️ About",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### 🧠 AI Status")
    st.caption(f"Model: {OLLAMA_MODEL}")
    st.caption("Knowledge: Your indexed books")
    st.caption("Search: FAISS semantic retrieval")

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.divider()
    st.caption("Built for reading, learning and discovery.")


# --------------------------------------------------
# TOP BANNER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-tag">READ SMARTER · LEARN DEEPER</div>
    <div class="hero-title">Your books. Your AI. Your knowledge.</div>
    <div class="hero-description">
        Ask questions about your indexed books and get understandable
        AI-generated answers supported by relevant passages and page
        references.
    </div>
    <div class="hero-spines" aria-hidden="true">
        <span></span><span></span><span></span><span></span><span></span><span></span><span></span>
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📚 Book collections", len(get_book_names()))

with col2:
    st.metric("🔎 Indexed passages", f"{index.ntotal:,}")

with col3:
    st.metric("🤖 AI model", "Qwen 2.5 · 3B")


# --------------------------------------------------
# CHAT PAGE
# --------------------------------------------------

if page == "💬 Chat":
    st.subheader("💬 Chat with your books")
    st.caption(
        "Ask a question. Transformer searches your books and writes "
        "an answer based on the relevant information."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history:
        st.markdown("### What would you like to learn?")
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📘</div>
                <div class="feature-title">Understand concepts</div>
                <div class="feature-text">
                    Ask for clear explanations of topics in your books.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Explore topics</div>
                <div class="feature-text">
                    Find relevant information across your collection.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📝</div>
                <div class="feature-title">Study smarter</div>
                <div class="feature-text">
                    Get explanations with book and page references.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("**Try asking:**")
        st.caption(
            "What is programming? · Explain computer architecture · "
            "Summarize the main ideas about algorithms."
        )

    # Display previous messages
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

            if item["role"] == "assistant":
                show_sources(item.get("sources", []))

    question = st.chat_input("Ask something about your books...")

    if question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                answer, sources = answer_question(question)
                st.markdown(answer)
                show_sources(sources)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            except urllib.error.URLError:
                st.error(
                    "I couldn't connect to Ollama. Make sure Ollama is "
                    "running on this computer, then try again."
                )

            except (TimeoutError, KeyError, ValueError, json.JSONDecodeError) as error:
                st.error(
                    "The AI could not finish this answer. "
                    "Please try again."
                )
                st.caption(f"Technical detail: {error}")

            except Exception as error:
                st.error("Something went wrong while generating the answer.")
                st.caption(f"Technical detail: {error}")


# --------------------------------------------------
# LIBRARY PAGE
# --------------------------------------------------

elif page == "📖 Library":
    st.subheader("📖 Your book library")
    st.caption("Explore the books included in your existing search index.")

    book_names = get_book_names()
    st.metric("Books available", len(book_names))

    for book_name in book_names:
        with st.expander(f"📕 {book_name}"):
            count = sum(
                1 for p in passages
                if p.get("book", "Unknown") == book_name
            )
            st.write(f"Searchable passages: **{count:,}**")

    st.info(
        "These are books already indexed in data/index. "
        "Adding and indexing new PDFs is a separate feature."
    )


# --------------------------------------------------
# SEARCH PAGE
# --------------------------------------------------

elif page == "🔎 Search":
    st.subheader("🔎 Search your knowledge base")
    st.caption(
        "Search directly for relevant passages without generating "
        "a full AI answer."
    )

    with st.form("book_search_form"):
        query = st.text_input(
            "Topic or question",
            placeholder="e.g. computer architecture, algorithms...",
        )
        submitted = st.form_submit_button(
            "Search books",
            use_container_width=True,
        )

    if submitted:
        if query.strip():
            show_search_results(query.strip())
        else:
            st.warning("Enter a topic or question first.")


# --------------------------------------------------
# SETTINGS PAGE
# --------------------------------------------------

elif page == "⚙️ Settings":
    st.subheader("⚙️ System settings")

    st.markdown("### AI configuration")
    st.write(f"**Language model:** {OLLAMA_MODEL}")
    st.write(f"**Ollama endpoint:** {OLLAMA_URL}")
    st.write("**Embeddings:** sentence-transformers/all-MiniLM-L6-v2")
    st.write("**Vector database:** FAISS")
    st.write("**PDF processing:** PyMuPDF")
    st.write("**Interface:** Streamlit")

    st.divider()
    st.markdown("### Knowledge base")
    st.write(f"**Indexed passages:** {index.ntotal:,}")
    st.write(f"**Book count:** {len(get_book_names())}")

    st.caption(
        "This app reuses your current index. Changing the AI model "
        "does not require rebuilding the book index."
    )


# --------------------------------------------------
# ABOUT PAGE
# --------------------------------------------------

elif page == "ℹ️ About":
    st.subheader("ℹ️ About Transformer")

    st.markdown("""
    Transformer is a local AI learning assistant that helps you explore
    information from your indexed book collection.

    **How it works**

    1. You ask a question.
    2. Semantic search finds relevant passages in your books.
    3. The Qwen AI model reads those passages and generates an answer.
    4. You can inspect the source passages and page references.

    **Privacy and limitations**

    - The language model runs locally through Ollama.
    - Answers depend on the quality and coverage of your indexed books.
    - AI-generated explanations can still contain errors, so verify
      important information against the displayed sources.
    """)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption(
    "TRANSFORMER AI  ·  LOCAL LANGUAGE MODEL  ·  "
    "RETRIEVAL-AUGMENTED GENERATION"
)

#python -m streamlit run app.py