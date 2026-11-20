"""
Resume vs. Job Description Rater

Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from analyzer import analyze_resume
from parser import extract_from_upload, extract_text_string

NAVY = "#1B365D"
SLATE = "#475569"
TEAL = "#2A6F7B"
RUST = "#A64436"
OFF_WHITE = "#F8F9FA"
WHITE = "#FFFFFF"
BORDER = "#E2E8F0"

st.set_page_config(
    page_title="Resume vs. Job Description Rater",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
    <style>
      html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: {OFF_WHITE};
        color: {NAVY};
      }}
      [data-testid="stHeader"] {{
        background: {OFF_WHITE};
      }}
      [data-testid="stSidebar"] {{
        display: none;
      }}
      [data-testid="stToolbar"] {{
        display: none;
      }}
      .block-container {{
        max-width: 920px;
        padding-top: 3.25rem;
        padding-bottom: 4.5rem;
        padding-left: 2.25rem;
        padding-right: 2.25rem;
      }}
      h1 {{
        font-size: 1.85rem;
        font-weight: 650;
        letter-spacing: -0.02em;
        color: {NAVY};
        margin-bottom: 0.35rem;
      }}
      .lede {{
        color: {SLATE};
        font-size: 1.02rem;
        line-height: 1.55;
        margin-bottom: 1.75rem;
      }}
      .section-label {{
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {SLATE};
        font-weight: 600;
        margin: 1.75rem 0 0.65rem 0;
      }}
      div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 0.35rem 0.15rem;
      }}
      .stButton > button {{
        background-color: {NAVY};
        color: {WHITE};
        border: 1px solid {NAVY};
        border-radius: 4px;
        padding: 0.55rem 1.35rem;
        font-weight: 600;
        letter-spacing: 0.01em;
      }}
      .stButton > button:hover {{
        background-color: #152a4a;
        border-color: #152a4a;
        color: {WHITE};
      }}
      .term-chip {{
        display: inline-block;
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 0.22rem 0.55rem;
        margin: 0 0.35rem 0.45rem 0;
        font-size: 0.86rem;
      }}
      .term-missing {{
        color: {RUST};
        border-color: #e8d5cf;
        background: #fbf7f5;
      }}
      .term-matched {{
        color: {TEAL};
        border-color: #d5e3e5;
        background: #f4f8f8;
      }}
      .gap-item {{
        color: {SLATE};
        line-height: 1.55;
        margin-bottom: 0.65rem;
      }}
      .footnote {{
        color: {SLATE};
        font-size: 0.85rem;
        margin-top: 2.5rem;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


def _plotly_layout(fig: go.Figure, height: int = 280) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(color=NAVY, family="Georgia, 'Times New Roman', serif", size=13),
        margin=dict(l=24, r=24, t=36, b=24),
        height=height,
    )
    return fig


def score_figure(score: int) -> go.Figure:
    """Navy gauge for the 0–100 match score."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"size": 36, "color": NAVY}},
            title={"text": "Match score", "font": {"size": 14, "color": SLATE}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": SLATE,
                    "tickfont": {"color": SLATE, "size": 11},
                },
                "bar": {"color": NAVY, "thickness": 0.28},
                "bgcolor": WHITE,
                "borderwidth": 1,
                "bordercolor": BORDER,
                "steps": [
                    {"range": [0, 50], "color": "#F1F5F9"},
                    {"range": [50, 75], "color": "#E8EEF2"},
                    {"range": [75, 100], "color": "#D9E2EA"},
                ],
                "threshold": {
                    "line": {"color": TEAL, "width": 2},
                    "thickness": 0.75,
                    "value": score,
                },
            },
        )
    )
    return _plotly_layout(fig, height=300)


def coverage_figure(matched_count: int, missing_count: int) -> go.Figure:
    """Horizontal comparison of matched vs. missing key terms."""
    fig = go.Figure(
        go.Bar(
            x=[matched_count, missing_count],
            y=["Matched terms", "Missing terms"],
            orientation="h",
            marker_color=[TEAL, RUST],
            marker_line_width=0,
            text=[matched_count, missing_count],
            textposition="outside",
            textfont={"color": SLATE, "size": 12},
            hoverinfo="x+y",
        )
    )
    fig.update_layout(
        title=dict(text="Keyword coverage", font=dict(size=14, color=SLATE)),
        xaxis=dict(
            title="",
            range=[0, max(matched_count, missing_count, 1) * 1.25],
            showgrid=True,
            gridcolor="#EEF2F6",
            zeroline=False,
            color=SLATE,
        ),
        yaxis=dict(title="", color=NAVY),
        bargap=0.45,
        showlegend=False,
    )
    return _plotly_layout(fig, height=220)


def render_chips(terms: list[str], kind: str) -> None:
    if not terms:
        st.caption("None identified.")
        return
    chips = "".join(
        f'<span class="term-chip term-{kind}">{term}</span>' for term in terms
    )
    st.markdown(chips, unsafe_allow_html=True)


st.title("Resume vs. Job Description Rater")
st.markdown(
    '<p class="lede">Compare a resume with a posting using local TF-IDF similarity '
    "and keyword overlap. Nothing is sent to an external model.</p>",
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.markdown("**Resume**")
        st.caption("PDF or Word document")
        resume_file = st.file_uploader(
            "Resume file",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            key="resume_upload",
        )

with right:
    with st.container(border=True):
        st.markdown("**Job description**")
        st.caption("Paste the posting, or upload a PDF / Word file")
        jd_text_input = st.text_area(
            "Job description text",
            height=160,
            placeholder="Paste the job description here…",
            label_visibility="collapsed",
            key="jd_text",
        )
        jd_file = st.file_uploader(
            "Job description file",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            key="jd_upload",
        )

st.write("")
run = st.button("Analyze Resume", type="primary")

if run:
    resume_text = ""
    jd_text = extract_text_string(jd_text_input)

    parse_error = None
    try:
        if resume_file is not None:
            resume_text = extract_from_upload(resume_file)
        if jd_file is not None:
            uploaded_jd = extract_from_upload(jd_file)
            jd_text = uploaded_jd if uploaded_jd else jd_text
    except ValueError as exc:
        parse_error = str(exc)
    except Exception:
        parse_error = "Could not read one of the files. Try exporting again as PDF or DOCX."

    missing_inputs = []
    if not resume_text:
        missing_inputs.append("a resume file (.pdf or .docx)")
    if not jd_text:
        missing_inputs.append("a job description (pasted text or an uploaded file)")

    if parse_error:
        st.error(parse_error)
    elif missing_inputs:
        st.warning("Add " + " and ".join(missing_inputs) + " before analyzing.")
    else:
        result = analyze_resume(resume_text, jd_text)
        score = int(result["score"])
        matched = result["matched_terms"]
        missing = result["missing_terms"]
        gaps = result["gaps"]

        st.markdown('<div class="section-label">Score</div>', unsafe_allow_html=True)
        chart_col, bar_col = st.columns((1.05, 1), gap="large")
        with chart_col:
            with st.container(border=True):
                st.plotly_chart(
                    score_figure(score),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
        with bar_col:
            with st.container(border=True):
                st.plotly_chart(
                    coverage_figure(len(matched), len(missing)),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

        st.markdown('<div class="section-label">Matched terms</div>', unsafe_allow_html=True)
        render_chips(matched, "matched")

        st.markdown('<div class="section-label">Missing terms</div>', unsafe_allow_html=True)
        render_chips(missing, "missing")

        st.markdown('<div class="section-label">Where the resume is thin</div>', unsafe_allow_html=True)
        with st.container(border=True):
            for item in gaps:
                st.markdown(f'<p class="gap-item">{item}</p>', unsafe_allow_html=True)

st.markdown(
    '<p class="footnote">Scoring is a local TF-IDF cosine similarity blended with '
    "keyword overlap. It is a drafting aid, not a hiring decision.</p>",
    unsafe_allow_html=True,
)
