
import os
import json
from typing import Any

import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Lead Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

REQUEST_TIMEOUT = 30


# ============================================================
# API CLIENT
# ============================================================

class APIError(Exception):
    """Raised when the backend API returns an error."""


def api_request(method: str, endpoint: str, payload=None):
    url = f"{API_BASE_URL}{endpoint}"

    try:
        response = requests.request(
            method=method,
            url=url,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        if not response.ok:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text

            raise APIError(
                f"API Error ({response.status_code}): {detail}"
            )

        if response.status_code == 204 or not response.content:
            return None

        try:
            return response.json()
        except ValueError:
            return response.text

    except requests.exceptions.ConnectionError:
        raise APIError(
            f"Backend se connection nahi ho raha. "
            f"Check karein ke API {API_BASE_URL} par running hai."
        )

    except requests.exceptions.Timeout:
        raise APIError("Backend request timeout ho gayi.")

    except requests.exceptions.RequestException as exc:
        raise APIError(str(exc))


def extract_records(data):
    """Handle list responses and common API response envelopes."""

    if data is None:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("items", "leads", "outreach", "results", "data"):
            value = data.get(key)

            if isinstance(value, list):
                return value

        return [data]

    return []


def get_leads():
    return extract_records(api_request("GET", "/leads/"))


def get_outreach():
    return extract_records(api_request("GET", "/outreach/"))


def create_lead(payload):
    return api_request("POST", "/leads/", payload)


def score_lead(lead_id):
    return api_request("POST", f"/leads/{lead_id}/score")


def enrich_lead(lead_id):
    return api_request("POST", f"/leads/{lead_id}/enrich")


def generate_outreach(lead_id, payload):
    return api_request(
        "POST",
        f"/outreach/{lead_id}/generate",
        payload,
    )


def update_outreach(outreach_id, payload):
    return api_request(
        "PUT",
        f"/outreach/{outreach_id}",
        payload,
    )


def approve_outreach(outreach_id):
    return api_request(
        "POST",
        f"/outreach/{outreach_id}/approve",
    )


def reject_outreach(outreach_id):
    return api_request(
        "POST",
        f"/outreach/{outreach_id}/reject",
    )


# ============================================================
# CUSTOM UI
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(40, 80, 160, 0.16), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(0, 210, 190, 0.08), transparent 25%),
            #080D18;
        color: #E8EDF7;
    }

    [data-testid="stSidebar"] {
        background: #0B1220;
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    [data-testid="stSidebar"] * {
        color: #DCE5F5;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        color: #F4F7FC !important;
        letter-spacing: -0.5px;
    }

    p, label, .stMarkdown {
        color: #B9C4D6;
    }

    .hero {
        padding: 28px 30px;
        border-radius: 22px;
        background:
            linear-gradient(115deg, rgba(20, 39, 70, 0.96), rgba(13, 26, 46, 0.92)),
            #101B2D;
        border: 1px solid rgba(120, 160, 220, 0.20);
        box-shadow: 0 15px 50px rgba(0,0,0,0.22);
        margin-bottom: 25px;
    }

    .hero-label {
        color: #5EEAD4;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero-title {
        font-size: 34px;
        line-height: 1.2;
        color: #FFFFFF;
        font-weight: 800;
        margin-top: 9px;
    }

    .hero-subtitle {
        color: #AABBD2;
        margin-top: 9px;
        font-size: 14px;
    }

    .metric-card {
        background: linear-gradient(145deg, #131F33, #0E1727);
        border: 1px solid rgba(148, 163, 184, 0.13);
        border-radius: 17px;
        padding: 19px 20px;
        min-height: 125px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .metric-label {
        color: #91A2BC;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-value {
        color: #F8FAFC;
        font-size: 29px;
        font-weight: 800;
        margin-top: 9px;
    }

    .metric-caption {
        color: #5EEAD4;
        font-size: 11px;
        margin-top: 5px;
    }

    .section-label {
        color: #5EEAD4;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    div[data-testid="stMetric"] {
        background: #111C2D;
        padding: 15px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.07);
    }

    div[data-testid="stMetricLabel"] {
        color: #9EADC3;
    }

    div[data-testid="stMetricValue"] {
        color: #FFFFFF;
    }

    .stButton button {
        border-radius: 10px;
        border: 1px solid rgba(94,234,212,0.28);
        background: linear-gradient(110deg, #0F766E, #0D9488);
        color: white;
        font-weight: 700;
        min-height: 42px;
        transition: 0.2s ease;
    }

    .stButton button:hover {
        border-color: #5EEAD4;
        background: linear-gradient(110deg, #115E59, #0F766E);
        transform: translateY(-1px);
    }

    .stTextInput input, .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"],
    .stNumberInput input {
        background: #111C2D;
        color: #FFFFFF;
        border-radius: 10px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 13px;
        overflow: hidden;
    }

    div[data-testid="stTabs"] button {
        color: #AFC0D5;
        font-weight: 700;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #5EEAD4;
    }

    .status-pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 30px;
        font-size: 11px;
        font-weight: 800;
        background: rgba(94,234,212,0.12);
        color: #5EEAD4;
    }

    .stAlert {
        border-radius: 12px;
    }

    hr {
        border-color: rgba(255,255,255,0.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def value_of(record, *keys, default=None):
    if not isinstance(record, dict):
        return default

    for key in keys:
        if record.get(key) is not None:
            return record[key]

    return default


def records_df(records):
    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


def numeric_series(df, column, default=0):
    if column in df.columns:
        return pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(default)

    return pd.Series(
        [default] * len(df),
        index=df.index,
        dtype="float64",
    )


def get_lead_name(lead):
    return (
        value_of(lead, "company_name", "company", "name", default="Unknown")
    )


def get_lead_id(lead):
    return value_of(lead, "id", "lead_id")


def get_outreach_id(item):
    return value_of(item, "id", "outreach_id")


def safe_status(value):
    return str(value or "unknown").strip().lower()


def display_table(df):
    if df.empty:
        st.info("Abhi display karne ke liye data available nahi hai.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


def metric_card(label, value, caption):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-label">AI LEAD INTELLIGENCE PLATFORM</div>
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=20, show_spinner=False)
def load_dashboard_data():
    leads = get_leads()
    outreach = get_outreach()
    return leads, outreach


def refresh_data():
    load_dashboard_data.clear()
    st.rerun()


try:
    with st.spinner("Loading intelligence data..."):
        leads, outreach = load_dashboard_data()

except APIError as exc:
    st.error(str(exc))
    st.info(
        "Backend start karein aur phir Refresh Data par click karein."
    )

    if st.button("Refresh Data"):
        refresh_data()

    st.stop()


leads_df = records_df(leads)
outreach_df = records_df(outreach)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding:10px 0 22px 0;">
            <div style="font-size:12px;color:#5EEAD4;font-weight:800;letter-spacing:2px;">
                ⚡ AI PLATFORM
            </div>
            <div style="font-size:22px;font-weight:800;color:white;margin-top:5px;">
                Lead Intelligence
            </div>
            <div style="font-size:11px;color:#8294AD;margin-top:5px;">
                SALES AUTOMATION SYSTEM
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Lead Management",
            "AI Intelligence",
            "Outreach Management",
            "Analytics",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("**SYSTEM STATUS**")
    st.markdown(
        '<span class="status-pill">● Dashboard Active</span>',
        unsafe_allow_html=True,
    )

    st.caption(f"API: {API_BASE_URL}")

    if st.button("↻ Refresh Data", use_container_width=True):
        refresh_data()

    st.divider()
    st.caption("AI Lead Intelligence Platform")


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    show_hero(
        "Your Sales Intelligence Command Center",
        "Monitor leads, AI scoring, enrichment and outreach performance from one place.",
    )

    total_leads = len(leads)
    total_outreach = len(outreach)

    scored_leads = sum(
        1 for lead in leads
        if value_of(lead, "ai_score", "score") is not None
    )

    approved = sum(
        1 for item in outreach
        if safe_status(value_of(item, "status")) == "approved"
    )

    pending = sum(
        1 for item in outreach
        if safe_status(value_of(item, "status")) in ("draft", "pending")
    )

    rejected = sum(
        1 for item in outreach
        if safe_status(value_of(item, "status")) == "rejected"
    )

    st.markdown('<div class="section-label">PERFORMANCE SNAPSHOT</div>',
                unsafe_allow_html=True)

    cols = st.columns(4)

    with cols[0]:
        metric_card("Total Leads", total_leads, "Leads in your database")

    with cols[1]:
        metric_card("AI Scored", scored_leads, "Leads with an AI score")

    with cols[2]:
        metric_card("Outreach", total_outreach, "Generated outreach records")

    with cols[3]:
        metric_card("Approved", approved, "Approved outreach records")

    st.write("")

    left, right = st.columns([1.5, 1])

    with left:
        st.subheader("Lead Intelligence Overview")

        if not leads_df.empty:
            score_col = (
                "ai_score"
                if "ai_score" in leads_df.columns
                else "score"
                if "score" in leads_df.columns
                else None
            )

            if score_col:
                chart_df = leads_df.copy()
                chart_df["AI Score"] = pd.to_numeric(
                    chart_df[score_col],
                    errors="coerce",
                )

                chart_df["Company"] = (
                    chart_df["company_name"]
                    if "company_name" in chart_df.columns
                    else chart_df.index.astype(str)
                )

                fig = px.bar(
                    chart_df.head(15),
                    x="Company",
                    y="AI Score",
                    color="AI Score",
                    color_continuous_scale=["#1E3A5F", "#0D9488", "#5EEAD4"],
                    template="plotly_dark",
                )

                fig.update_layout(
                    height=360,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=20, b=10),
                    xaxis_title="",
                    yaxis_title="AI Score",
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("AI score data abhi available nahi hai.")
        else:
            st.info("Abhi koi lead available nahi hai.")

    with right:
        st.subheader("Outreach Status")

        if outreach:
            status_counts = {}

            for item in outreach:
                status = safe_status(
                    value_of(item, "status", default="unknown")
                )
                status_counts[status] = status_counts.get(status, 0) + 1

            fig = px.pie(
                names=list(status_counts.keys()),
                values=list(status_counts.values()),
                hole=0.68,
                color_discrete_sequence=[
                    "#5EEAD4",
                    "#60A5FA",
                    "#FBBF24",
                    "#F87171",
                    "#A78BFA",
                ],
                template="plotly_dark",
            )

            fig.update_layout(
                height=310,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=5, r=5, t=10, b=5),
                showlegend=True,
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Outreach records abhi available nahi hain.")

    st.subheader("Recent Leads")

    if leads:
        recent_df = pd.DataFrame([
            {
                "ID": get_lead_id(lead),
                "Company": get_lead_name(lead),
                "Contact": value_of(lead, "contact_name", "name", default="-"),
                "Email": value_of(lead, "email", default="-"),
                "AI Score": value_of(lead, "ai_score", "score", default="-"),
                "Status": value_of(lead, "status", default="-"),
            }
            for lead in leads[:8]
        ])

        display_table(recent_df)
    else:
        st.info("No leads found.")


# ============================================================
# LEAD MANAGEMENT
# ============================================================

elif page == "Lead Management":

    show_hero(
        "Lead Management",
        "Create, organize and manage your sales prospects.",
    )

    tab1, tab2 = st.tabs(["All Leads", "Add New Lead"])

    with tab1:

        st.subheader("Lead Database")

        if leads:
            search = st.text_input(
                "Search leads",
                placeholder="Search company, contact or email...",
            )

            filtered_leads = leads

            if search:
                filtered_leads = [
                    lead for lead in leads
                    if search.lower() in json.dumps(
                        lead,
                        default=str,
                    ).lower()
                ]

            table_data = []

            for lead in filtered_leads:
                table_data.append({
                    "ID": get_lead_id(lead),
                    "Company": get_lead_name(lead),
                    "Contact": value_of(lead, "contact_name", default="-"),
                    "Email": value_of(lead, "email", default="-"),
                    "Industry": value_of(lead, "industry", default="-"),
                    "AI Score": value_of(lead, "ai_score", "score", default="-"),
                    "Status": value_of(lead, "status", default="-"),
                })

            display_table(pd.DataFrame(table_data))

            st.divider()
            st.subheader("Lead Actions")

            selectable = [
                lead for lead in filtered_leads
                if get_lead_id(lead) is not None
            ]

            if selectable:
                selected = st.selectbox(
                    "Select a lead",
                    selectable,
                    format_func=lambda x: (
                        f"#{get_lead_id(x)} — {get_lead_name(x)}"
                    ),
                    key="lead_management_selected",
                )

                selected_id = get_lead_id(selected)

                action1, action2 = st.columns(2)

                with action1:
                    if st.button(
                        "⚡ Run AI Scoring",
                        use_container_width=True,
                    ):
                        try:
                            with st.spinner("Scoring lead..."):
                                result = score_lead(selected_id)

                            st.success("AI scoring completed.")
                            if result is not None:
                                st.json(result)

                            load_dashboard_data.clear()

                        except APIError as exc:
                            st.error(str(exc))

                with action2:
                    if st.button(
                        "🔍 Enrich Lead",
                        use_container_width=True,
                    ):
                        try:
                            with st.spinner("Enriching lead..."):
                                result = enrich_lead(selected_id)

                            st.success("Lead enrichment completed.")
                            if result is not None:
                                st.json(result)

                            load_dashboard_data.clear()

                        except APIError as exc:
                            st.error(str(exc))

        else:
            st.info("No leads found. Add your first lead.")

    with tab2:

        st.subheader("Create a New Lead")

        with st.form("create_lead_form"):

            col1, col2 = st.columns(2)

            with col1:
                company_name = st.text_input(
                    "Company Name *",
                    placeholder="Example: Acme Technologies",
                )

                contact_name = st.text_input(
                    "Contact Name",
                    placeholder="Example: John Smith",
                )

                email = st.text_input(
                    "Email",
                    placeholder="john@company.com",
                )

            with col2:
                website = st.text_input(
                    "Website",
                    placeholder="https://company.com",
                )

                industry = st.text_input(
                    "Industry",
                    placeholder="Technology",
                )

                source = st.selectbox(
                    "Lead Source",
                    ["Website", "LinkedIn", "Referral", "Manual", "Other"],
                )

            notes = st.text_area(
                "Notes",
                placeholder="Add relevant information about this lead...",
            )

            submitted = st.form_submit_button(
                "＋ Create Lead",
                use_container_width=True,
            )

            if submitted:

                if not company_name.strip():
                    st.warning("Company name required hai.")

                else:
                    payload = {
                        "company_name": company_name.strip(),
                        "contact_name": contact_name.strip(),
                        "email": email.strip(),
                        "website": website.strip(),
                        "industry": industry.strip(),
                        "source": source,
                        "notes": notes.strip(),
                    }

                    try:
                        with st.spinner("Creating lead..."):
                            result = create_lead(payload)

                        st.success("Lead created successfully.")

                        if result is not None:
                            st.json(result)

                        load_dashboard_data.clear()

                    except APIError as exc:
                        st.error(str(exc))


# ============================================================
# AI INTELLIGENCE
# ============================================================

elif page == "AI Intelligence":

    show_hero(
        "AI Intelligence Engine",
        "Understand lead quality, scoring and enrichment insights.",
    )

    if not leads:
        st.info("AI Intelligence ke liye pehle leads add karein.")
    else:

        selectable = [
            lead for lead in leads
            if get_lead_id(lead) is not None
        ]

        selected = st.selectbox(
            "Select lead for AI analysis",
            selectable,
            format_func=lambda x: (
                f"#{get_lead_id(x)} — {get_lead_name(x)}"
            ),
            key="ai_selected_lead",
        )

        selected_id = get_lead_id(selected)

        score = value_of(selected, "ai_score", "score", default=0)
        confidence = value_of(
            selected,
            "ai_confidence",
            "confidence",
            default=0,
        )

        try:
            score = float(score or 0)
        except (ValueError, TypeError):
            score = 0

        try:
            confidence = float(confidence or 0)
        except (ValueError, TypeError):
            confidence = 0

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card("AI Score", score, "Current lead score")

        with c2:
            metric_card("AI Confidence", confidence, "Model confidence")

        with c3:
            metric_card(
                "Lead Status",
                str(value_of(selected, "status", default="Unknown")).title(),
                "Current database status",
            )

        st.divider()

        left, right = st.columns([1, 1])

        with left:
            st.subheader("AI Scoring")

            st.write(
                "AI scoring backend ko lead ki quality evaluate karne ke liye call karta hai."
            )

            if st.button(
                "⚡ Analyze Lead",
                use_container_width=True,
            ):
                try:
                    with st.spinner("AI is analyzing this lead..."):
                        result = score_lead(selected_id)

                    st.success("AI analysis completed.")

                    if result is not None:
                        st.json(result)

                    load_dashboard_data.clear()

                except APIError as exc:
                    st.error(str(exc))

        with right:
            st.subheader("Lead Enrichment")

            st.write(
                "Enrichment action backend ke configured data sources se lead information update kar sakta hai."
            )

            if st.button(
                "🔍 Enrich Lead Data",
                use_container_width=True,
            ):
                try:
                    with st.spinner("Enriching lead data..."):
                        result = enrich_lead(selected_id)

                    st.success("Enrichment request completed.")

                    if result is not None:
                        st.json(result)

                    load_dashboard_data.clear()

                except APIError as exc:
                    st.error(str(exc))

        st.divider()

        st.subheader("Selected Lead Information")

        st.json(selected)


# ============================================================
# OUTREACH MANAGEMENT
# ============================================================

elif page == "Outreach Management":

    show_hero(
        "Outreach Command Center",
        "Generate, review, edit and manage AI-powered sales outreach.",
    )

    tab1, tab2 = st.tabs(["Outreach Records", "Generate Outreach"])

    with tab1:

        st.subheader("Outreach Pipeline")

        if outreach:

            status_filter = st.selectbox(
                "Filter by status",
                [
                    "All",
                    "draft",
                    "pending",
                    "approved",
                    "rejected",
                    "sent",
                ],
            )

            filtered = outreach

            if status_filter != "All":
                filtered = [
                    item for item in outreach
                    if safe_status(value_of(item, "status")) == status_filter
                ]

            outreach_table = []

            for item in filtered:
                outreach_table.append({
                    "ID": get_outreach_id(item),
                    "Lead ID": value_of(item, "lead_id", default="-"),
                    "Channel": value_of(item, "channel", default="-"),
                    "Status": value_of(item, "status", default="-"),
                    "Subject": value_of(item, "subject", default="-"),
                    "Created": value_of(
                        item,
                        "created_at",
                        "created",
                        default="-",
                    ),
                })

            display_table(pd.DataFrame(outreach_table))

            st.divider()
            st.subheader("Manage Outreach")

            selectable_outreach = [
                item for item in filtered
                if get_outreach_id(item) is not None
            ]

            if selectable_outreach:

                selected_outreach = st.selectbox(
                    "Select outreach record",
                    selectable_outreach,
                    format_func=lambda x: (
                        f"#{get_outreach_id(x)} — "
                        f"{value_of(x, 'status', default='unknown')} — "
                        f"Lead {value_of(x, 'lead_id', default='?')}"
                    ),
                    key="selected_outreach_record",
                )

                outreach_id = get_outreach_id(selected_outreach)

                st.markdown("**Outreach Content**")

                subject = st.text_input(
                    "Subject",
                    value=str(value_of(
                        selected_outreach,
                        "subject",
                        default="",
                    )),
                    key=f"subject_{outreach_id}",
                )

                body = st.text_area(
                    "Message",
                    value=str(value_of(
                        selected_outreach,
                        "body",
                        "content",
                        "message",
                        default="",
                    )),
                    height=220,
                    key=f"body_{outreach_id}",
                )

                if st.button(
                    "💾 Save Changes",
                    use_container_width=True,
                ):

                    try:
                        payload = {
                            "subject": subject,
                            "body": body,
                        }

                        update_outreach(outreach_id, payload)

                        st.success("Outreach updated successfully.")
                        load_dashboard_data.clear()

                    except APIError as exc:
                        st.error(str(exc))

                status = safe_status(
                    value_of(selected_outreach, "status")
                )

                st.divider()

                col1, col2 = st.columns(2)

                with col1:
                    if status not in ("approved", "rejected", "sent"):

                        if st.button(
                            "✓ Approve Outreach",
                            use_container_width=True,
                        ):
                            try:
                                approve_outreach(outreach_id)

                                st.success(
                                    "Outreach approved. "
                                    "It is ready for a sending integration; "
                                    "approval itself does not send the message."
                                )

                                load_dashboard_data.clear()

                            except APIError as exc:
                                st.error(str(exc))

                with col2:
                    if status not in ("rejected", "sent"):

                        if st.button(
                            "✕ Reject Outreach",
                            use_container_width=True,
                        ):
                            try:
                                reject_outreach(outreach_id)

                                st.success("Outreach rejected.")
                                load_dashboard_data.clear()

                            except APIError as exc:
                                st.error(str(exc))

        else:
            st.info("No outreach records found.")

    with tab2:

        st.subheader("Generate AI Outreach")

        if not leads:
            st.info("Outreach generate karne ke liye pehle lead create karein.")

        else:

            selectable = [
                lead for lead in leads
                if get_lead_id(lead) is not None
            ]

            selected_lead = st.selectbox(
                "Select target lead",
                selectable,
                format_func=lambda x: (
                    f"#{get_lead_id(x)} — {get_lead_name(x)}"
                ),
                key="outreach_target_lead",
            )

            channel = st.selectbox(
                "Outreach Channel",
                ["email", "linkedin", "whatsapp"],
            )

            tone = st.selectbox(
                "Communication Tone",
                ["professional", "friendly", "persuasive", "formal"],
            )

            objective = st.text_area(
                "Outreach Objective",
                placeholder=(
                    "Example: Introduce our AI automation services "
                    "and schedule a discovery call."
                ),
            )

            if st.button(
                "✨ Generate AI Outreach",
                use_container_width=True,
            ):

                payload = {
                    "channel": channel,
                    "tone": tone,
                    "objective": objective,
                }

                try:
                    with st.spinner("Generating personalized outreach..."):
                        result = generate_outreach(
                            get_lead_id(selected_lead),
                            payload,
                        )

                    st.success("Outreach generated successfully.")

                    if result is not None:
                        st.json(result)

                    load_dashboard_data.clear()

                except APIError as exc:
                    st.error(str(exc))


# ============================================================
# ANALYTICS
# ============================================================

elif page == "Analytics":

    show_hero(
        "Advanced Sales Analytics",
        "Explore lead performance, AI scoring patterns and outreach activity.",
    )

    if not leads:
        st.info("Analytics ke liye leads data available nahi hai.")

    else:

        analytics_df = leads_df.copy()

        analytics_df["AI Score"] = numeric_series(
            analytics_df,
            "ai_score",
        )

        if "ai_score" not in analytics_df.columns:
            analytics_df["AI Score"] = numeric_series(
                analytics_df,
                "score",
            )

        analytics_df["AI Confidence"] = numeric_series(
            analytics_df,
            "ai_confidence",
        )

        analytics_df["Company"] = (
            analytics_df["company_name"]
            if "company_name" in analytics_df.columns
            else analytics_df.index.astype(str)
        )

        analytics_df["Industry"] = (
            analytics_df["industry"]
            if "industry" in analytics_df.columns
            else "Unknown"
        )

        analytics_df["Status"] = (
            analytics_df["status"]
            if "status" in analytics_df.columns
            else "Unknown"
        )

        # A transparent derived indicator, not a model-generated score.
        analytics_df["Quality Proxy"] = (
            analytics_df["AI Score"] * 0.7
            + analytics_df["AI Confidence"] * 0.3
        )

        st.markdown(
            '<div class="section-label">KEY PERFORMANCE INDICATORS</div>',
            unsafe_allow_html=True,
        )

        avg_score = (
            analytics_df["AI Score"].mean()
            if len(analytics_df) else 0
        )

        avg_confidence = (
            analytics_df["AI Confidence"].mean()
            if len(analytics_df) else 0
        )

        high_score_count = int(
            (analytics_df["AI Score"] >= 70).sum()
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card("Average AI Score", f"{avg_score:.1f}", "Across available leads")

        with c2:
            metric_card("Average Confidence", f"{avg_confidence:.1f}", "Across available leads")

        with c3:
            metric_card("High Score Leads", high_score_count, "AI score of 70 or above")

        with c4:
            metric_card("Total Outreach", len(outreach), "Outreach records")

        st.write("")

        # ----------------------------------------------------
        # 3D ANALYTICS
        # ----------------------------------------------------

        st.subheader("🌐 3D Lead Intelligence Map")

        st.caption(
            "X = AI Score | Y = AI Confidence | "
            "Z = Quality Proxy (derived from score and confidence)"
        )

        plot_df = analytics_df.copy()

        plot_df["AI Score"] = pd.to_numeric(
            plot_df["AI Score"],
            errors="coerce",
        ).fillna(0)

        plot_df["AI Confidence"] = pd.to_numeric(
            plot_df["AI Confidence"],
            errors="coerce",
        ).fillna(0)

        plot_df["Quality Proxy"] = pd.to_numeric(
            plot_df["Quality Proxy"],
            errors="coerce",
        ).fillna(0)

        fig_3d = px.scatter_3d(
            plot_df,
            x="AI Score",
            y="AI Confidence",
            z="Quality Proxy",
            color="Industry",
            hover_name="Company",
            hover_data=["Status"],
            size_max=15,
            opacity=0.85,
            template="plotly_dark",
        )

        fig_3d.update_traces(
            marker=dict(
                size=7,
                line=dict(width=0.5, color="#FFFFFF"),
            )
        )

        fig_3d.update_layout(
            height=620,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=15, b=0),
            scene=dict(
                bgcolor="rgba(0,0,0,0)",
                xaxis_title="AI Score",
                yaxis_title="AI Confidence",
                zaxis_title="Quality Proxy",
                xaxis=dict(
                    backgroundcolor="#0D1728",
                    gridcolor="#25364D",
                    zerolinecolor="#25364D",
                ),
                yaxis=dict(
                    backgroundcolor="#0D1728",
                    gridcolor="#25364D",
                    zerolinecolor="#25364D",
                ),
                zaxis=dict(
                    backgroundcolor="#0D1728",
                    gridcolor="#25364D",
                    zerolinecolor="#25364D",
                ),
            ),
            legend_title="Industry",
        )

        st.plotly_chart(
            fig_3d,
            use_container_width=True,
        )

        st.caption(
            "Note: Quality Proxy is a dashboard-derived indicator, "
            "not an independently generated AI quality score."
        )

        st.divider()

        # ----------------------------------------------------
        # 2D CHARTS
        # ----------------------------------------------------

        left, right = st.columns(2)

        with left:

            st.subheader("AI Score Distribution")

            fig_score = px.histogram(
                analytics_df,
                x="AI Score",
                nbins=15,
                color_discrete_sequence=["#14B8A6"],
                template="plotly_dark",
            )

            fig_score.update_layout(
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=20, b=10),
            )

            st.plotly_chart(
                fig_score,
                use_container_width=True,
            )

        with right:

            st.subheader("Industry Breakdown")

            industry_counts = (
                analytics_df["Industry"]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .reset_index()
            )

            industry_counts.columns = ["Industry", "Leads"]

            fig_industry = px.bar(
                industry_counts,
                x="Industry",
                y="Leads",
                color="Leads",
                color_continuous_scale=["#164E63", "#0D9488", "#5EEAD4"],
                template="plotly_dark",
            )

            fig_industry.update_layout(
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=20, b=10),
                showlegend=False,
            )

            st.plotly_chart(
                fig_industry,
                use_container_width=True,
            )

        # ----------------------------------------------------
        # OUTREACH ANALYTICS
        # ----------------------------------------------------

        st.divider()
        st.subheader("Outreach Performance")

        if outreach:

            outreach_status = pd.DataFrame([
                {
                    "Status": str(
                        value_of(item, "status", default="Unknown")
                    ).title(),
                    "Channel": str(
                        value_of(item, "channel", default="Unknown")
                    ).title(),
                }
                for item in outreach
            ])

            left, right = st.columns(2)

            with left:

                status_counts = (
                    outreach_status["Status"]
                    .value_counts()
                    .reset_index()
                )

                status_counts.columns = ["Status", "Count"]

                fig_status = px.bar(
                    status_counts,
                    x="Status",
                    y="Count",
                    color="Status",
                    template="plotly_dark",
                    color_discrete_sequence=[
                        "#5EEAD4",
                        "#60A5FA",
                        "#FBBF24",
                        "#F87171",
                        "#A78BFA",
                    ],
                )

                fig_status.update_layout(
                    height=330,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=20, b=10),
                    showlegend=False,
                )

                st.plotly_chart(
                    fig_status,
                    use_container_width=True,
                )

            with right:

                channel_counts = (
                    outreach_status["Channel"]
                    .value_counts()
                    .reset_index()
                )

                channel_counts.columns = ["Channel", "Count"]

                fig_channel = px.pie(
                    channel_counts,
                    names="Channel",
                    values="Count",
                    hole=0.6,
                    template="plotly_dark",
                    color_discrete_sequence=[
                        "#5EEAD4",
                        "#60A5FA",
                        "#A78BFA",
                    ],
                )

                fig_channel.update_layout(
                    height=330,
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=20, b=10),
                )

                st.plotly_chart(
                    fig_channel,
                    use_container_width=True,
                )

        else:
            st.info("Outreach analytics ke liye records available nahi hain.")

        # ----------------------------------------------------
        # EXPORT
        # ----------------------------------------------------

        st.divider()
        st.subheader("Export Analytics Data")

        csv_data = analytics_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Lead Analytics CSV",
            data=csv_data,
            file_name="lead_analytics.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        margin-top:45px;
        padding:18px 0;
        border-top:1px solid rgba(255,255,255,0.08);
        text-align:center;
        color:#71829A;
        font-size:11px;
    ">
        AI LEAD INTELLIGENCE PLATFORM · SALES AUTOMATION & ANALYTICS
    </div>
    """,
    unsafe_allow_html=True,
)
