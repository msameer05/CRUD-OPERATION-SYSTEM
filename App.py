from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FileFlow | File Manager",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

STORAGE = Path(__file__).resolve().parent / "storage"
STORAGE.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-top: 2rem; max-width: 1100px;}

    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%);
        padding: 2rem 2.2rem;
        border-radius: 18px;
        color: #fff;
        margin-bottom: 1.6rem;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.25);
    }
    .hero h1 {margin: 0; font-size: 2.1rem; font-weight: 800; letter-spacing: -0.5px;}
    .hero p {margin: .4rem 0 0; opacity: .85; font-size: 1.02rem;}

    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }
    .metric-card .label {color: #6b7280; font-size: .8rem; text-transform: uppercase; letter-spacing: .08em;}
    .metric-card .value {color: #0f172a; font-size: 1.7rem; font-weight: 700; margin-top: .2rem;}

    .section-title {font-size: 1.25rem; font-weight: 700; margin: .4rem 0 .8rem; color: #0f172a;}

    div.stButton > button, div.stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button {
        border-radius: 10px;
        font-weight: 600;
        padding: .55rem 1.2rem;
    }
    section[data-testid="stSidebar"] {background: #0f172a;}
    section[data-testid="stSidebar"] * {color: #e2e8f0 !important;}
    .footer {text-align: center; color: #9ca3af; font-size: .85rem; margin-top: 3rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def flash(kind: str, message: str) -> None:
    st.session_state["flash"] = (kind, message)


def show_flash() -> None:
    item = st.session_state.pop("flash", None)
    if item:
        kind, message = item
        getattr(st, kind)(message)


def clean_name(name: str):
    """Validate a file name. Returns (name, error)."""
    name = (name or "").strip()
    if not name:
        return None, "File name cannot be empty."
    if name != Path(name).name or name.startswith("."):
        return None, "Invalid file name. Folders and hidden names are not allowed."
    if "." not in name:
        name += ".txt"
    return name, None


def get_path(name: str) -> Path:
    return STORAGE / name


def human_size(num: int) -> str:
    size = float(num)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def list_files():
    return sorted([p for p in STORAGE.iterdir() if p.is_file()], key=lambda p: p.name.lower())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def metric(label: str, value: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="label">{label}</div>'
        f'<div class="value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def file_picker(key: str):
    files = list_files()
    if not files:
        st.info("No files yet. Create your first file from the **Create** page.")
        return None
    return st.selectbox("Select a file", [f.name for f in files], key=key)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_dashboard():
    files = list_files()
    total_size = sum(f.stat().st_size for f in files)
    latest = max((f.stat().st_mtime for f in files), default=None)

    c1, c2, c3 = st.columns(3)
    with c1:
        metric("Total files", str(len(files)))
    with c2:
        metric("Storage used", human_size(total_size))
    with c3:
        metric("Last modified", datetime.fromtimestamp(latest).strftime("%d %b, %H:%M") if latest else "—")

    st.markdown('<div class="section-title" style="margin-top:1.6rem">Your files</div>', unsafe_allow_html=True)
    if not files:
        st.info("Your workspace is empty. Head to **Create** to add a file.")
        return

    df = pd.DataFrame(
        [
            {
                "Name": f.name,
                "Size": human_size(f.stat().st_size),
                "Modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            }
            for f in files
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)


def page_create():
    st.markdown('<div class="section-title">Create a new file</div>', unsafe_allow_html=True)
    with st.form("create_form", clear_on_submit=True):
        name = st.text_input("File name", placeholder="notes.txt")
        data = st.text_area("Content", height=240, placeholder="Write something...")
        submitted = st.form_submit_button("Create file", type="primary")

    if submitted:
        name, err = clean_name(name)
        if err:
            st.error(err)
        elif get_path(name).exists():
            st.error(f"`{name}` already exists.")
        else:
            get_path(name).write_text(data, encoding="utf-8")
            flash("success", f"`{name}` created successfully.")
            st.rerun()


def page_read():
    st.markdown('<div class="section-title">Read a file</div>', unsafe_allow_html=True)
    name = file_picker("read_pick")
    if not name:
        return
    path = get_path(name)
    content = read_text(path)

    c1, c2 = st.columns(2)
    with c1:
        metric("Size", human_size(path.stat().st_size))
    with c2:
        metric("Characters", f"{len(content):,}")

    st.write("")
    st.code(content or "(empty file)", language=None, wrap_lines=True)
    st.download_button("Download file", content, file_name=name)


def page_update():
    st.markdown('<div class="section-title">Update a file</div>', unsafe_allow_html=True)
    name = file_picker("update_pick")
    if not name:
        return
    path = get_path(name)

    tab_rename, tab_append, tab_overwrite = st.tabs(["✏️ Rename", "➕ Append", "📝 Overwrite"])

    with tab_rename:
        new_name = st.text_input("New file name", value=name, key="rename_input")
        if st.button("Rename file", type="primary"):
            new_name, err = clean_name(new_name)
            if err:
                st.error(err)
            elif new_name == name:
                st.warning("The new name is the same as the current one.")
            elif get_path(new_name).exists():
                st.error(f"`{new_name}` already exists.")
            else:
                path.rename(get_path(new_name))
                flash("success", f"Renamed `{name}` to `{new_name}`.")
                st.rerun()

    with tab_append:
        extra = st.text_area("Text to append", height=160, key="append_input")
        if st.button("Append content", type="primary"):
            if not extra:
                st.warning("Nothing to append.")
            else:
                with path.open("a", encoding="utf-8") as f:
                    f.write("\n" + extra)
                flash("success", f"Content appended to `{name}`.")
                st.rerun()

    with tab_overwrite:
        new_content = st.text_area("New content", value=read_text(path), height=240, key=f"over_{name}")
        if st.button("Overwrite file", type="primary"):
            path.write_text(new_content, encoding="utf-8")
            flash("success", f"`{name}` overwritten.")
            st.rerun()


def page_delete():
    st.markdown('<div class="section-title">Delete a file</div>', unsafe_allow_html=True)
    name = file_picker("delete_pick")
    if not name:
        return
    st.warning(f"You are about to permanently delete `{name}`. This cannot be undone.")
    confirm = st.checkbox("I understand, delete this file")
    if st.button("Delete file", type="primary", disabled=not confirm):
        get_path(name).unlink()
        flash("success", f"`{name}` deleted.")
        st.rerun()


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
PAGES = {
    "📊  Dashboard": page_dashboard,
    "➕  Create": page_create,
    "📖  Read": page_read,
    "✏️  Update": page_update,
    "🗑️  Delete": page_delete,
}

with st.sidebar:
    st.markdown("## 📁 FileFlow")
    st.caption("Simple, safe file management")
    st.write("")
    choice = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    st.write("")
    st.caption(f"Workspace: `{STORAGE.name}/`")

st.markdown(
    """
    <div class="hero">
        <h1>FileFlow</h1>
        <p>Create, read, update and delete files from a clean, modern interface.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

show_flash()
PAGES[choice]()

st.markdown('<div class="footer">Built with Python &amp; Streamlit</div>', unsafe_allow_html=True)