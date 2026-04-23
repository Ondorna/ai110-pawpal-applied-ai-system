import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from rag_engine import generate_advice, estimate_confidence
import uuid
import os

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(160deg, #fff0f6 0%, #fce4f5 50%, #ffe8f0 100%);
}
header[data-testid="stHeader"] { background: transparent; }
.main-title {
    text-align: center; font-size: 3rem; font-weight: 800;
    color: #d63384; letter-spacing: 2px; margin-bottom: 0.2em;
}
.main-subtitle {
    text-align: center; font-size: 1.1rem;
    color: #e683b0; margin-bottom: 2em;
}
.section-title {
    font-size: 1.3rem; font-weight: 700; color: #c2185b;
    margin: 1.5em 0 0.5em 0; padding-left: 0.5em;
    border-left: 4px solid #f48fb1;
}
.task-card {
    background: white; border-radius: 20px; padding: 1em 1.5em;
    margin-bottom: 0.8em; border: 1.5px solid #f8bbd0;
    box-shadow: 0 4px 15px rgba(233,30,99,0.08);
}
.task-title { font-size: 1.1rem; font-weight: 700; color: #880e4f; }
.task-meta { font-size: 0.9rem; color: #ad1457; margin-top: 0.3em; }
.task-status { font-size: 0.85rem; margin-top: 0.3em; color: #c2185b; }
.conflict-box {
    background: #fff0f3; border: 2px solid #f48fb1; border-radius: 15px;
    padding: 0.8em 1.2em; margin-bottom: 0.8em; color: #c2185b; font-weight: 600;
}
.advice-box {
    background: white; border-radius: 20px; padding: 1.5em;
    border: 2px solid #f48fb1; color: #880e4f; font-size: 1rem; line-height: 1.7;
}
div.stButton > button {
    background: linear-gradient(90deg, #f06292, #e91e8c);
    color: white; border: none; border-radius: 25px;
    padding: 0.6em 2em; font-weight: 700; font-size: 1rem;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    border-radius: 12px; border: 1.5px solid #f48fb1;
    background: #fff8fb; color: #880e4f;
}
div[data-testid="stSelectbox"] > div > div {
    border-radius: 12px; border: 1.5px solid #f48fb1;
    background: #fff8fb; color: #880e4f;
}
div[data-testid="stRadio"] label p { color: #c2185b; font-weight: 600; }
label { color: #c2185b; font-weight: 600; }
hr { border-color: #f8bbd0; }
div[data-testid="stAlert"] {
    background: #fff0f6; border: 1.5px solid #f48fb1;
    border-radius: 15px; color: #c2185b;
}
p, span, div { color: #880e4f; }
            
            div.stButton > button:hover {
    background: linear-gradient(90deg, #e91e8c, #c2185b);
    transform: translateY(-2px);
    cursor: pointer;
}

div[data-testid="stSelectbox"]:hover > div > div {
    border-color: #c2185b;
    background: #fff0f6;
}

div[data-testid="stTextInput"]:hover input,
div[data-testid="stNumberInput"]:hover input {
    border-color: #c2185b;
    background: #fff0f6;
}

div[data-testid="stRadio"] label:hover p {
    color: #d63384;
    cursor: pointer;
}

a:hover {
    color: #d63384;
    text-decoration: underline;
}

.task-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(233,30,99,0.15);
    cursor: pointer;
}
* { transition: all 0.2s; }

button:hover, 
[role="button"]:hover,
label:hover,
select:hover,
input:hover,
a:hover,
.task-card:hover,
[data-testid="stSelectbox"]:hover,
[data-testid="stRadio"] label:hover p,
[data-testid="stTab"]:hover {
    opacity: 0.75;
    cursor: pointer;
}

pre, code, [data-testid="stText"] {
    color: #880e4f;
}
</style>
            

""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🐾 PawPal+</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">🌸 Your cozy pet care planner — making every day special! 🌸</div>', unsafe_allow_html=True)
st.divider()

# ── Session state ─────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    if os.path.exists("data.json"):
        st.session_state.owner = Owner.load_from_json("data.json")
    else:
        st.session_state.owner = Owner(name="Jordan")
        st.session_state.owner.add_pet(Pet(name="Mochi", species="dog", age=3))

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋 Task Planner", "🤖 AI Care Advice"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — original task planner (unchanged)
# ═══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">🏠 Owner & Pet Info</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        owner_name = st.text_input("👤 Owner name", value=st.session_state.owner.name)
        st.session_state.owner.name = owner_name
    with col2:
        pet_name = st.text_input("🐾 Pet name",
            value=st.session_state.owner.pets[0].name if st.session_state.owner.pets else "Mochi")
    with col3:
        species = st.selectbox("🐶 Species", ["dog", "cat", "other"])

    pet = next((p for p in st.session_state.owner.pets if p.name == pet_name), None)
    if not pet:
        pet = Pet(name=pet_name, species=species, age=1)
        st.session_state.owner.add_pet(pet)

    st.divider()
    st.markdown('<div class="section-title">✏️ Add a New Task</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("📝 Task title", value="Morning walk")
    with col2:
        duration = st.number_input("⏱ Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("⭐ Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        time = st.text_input("🕐 Time (HH:MM)", value="08:00")
    with col5:
        frequency = st.selectbox("🔁 Frequency", ["once", "daily", "weekly"])

    if st.button("➕ Add Task", use_container_width=True):
        task = Task(
            task_id=str(uuid.uuid4()),
            description=task_title,
            time=time,
            duration=int(duration),
            priority=priority,
            frequency=frequency
        )
        pet.add_task(task)
        st.session_state.owner.save_to_json("data.json")
        st.success(f"🌸 Added **{task_title}** to **{pet.name}**!")

    st.divider()

    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    sort_mode = st.radio("📋 Sort tasks by:", ["By Time 🕐", "By Priority ⭐"], horizontal=True)

    if pet.tasks:
        st.markdown(f'<div class="section-title">🐾 {pet.name}\'s Tasks</div>', unsafe_allow_html=True)
        if sort_mode == "By Time 🕐":
            sorted_tasks = sorted(pet.tasks, key=lambda t: t.time)
        else:
            p_order = {"high": 0, "medium": 1, "low": 2}
            sorted_tasks = sorted(pet.tasks, key=lambda t: p_order.get(t.priority, 3))

        for t in sorted_tasks:
            emoji = priority_emoji.get(t.priority, "")
            status = "✅ Complete" if t.is_complete else "🔘 Pending"
            st.markdown(f"""
            <div class="task-card">
                <div class="task-title">{emoji} {t.description}</div>
                <div class="task-meta">🕐 {t.time} &nbsp;|&nbsp; ⏱ {t.duration} min &nbsp;|&nbsp; 🔁 {t.frequency.capitalize()}</div>
                <div class="task-status">{status} &nbsp;|&nbsp; Priority: {t.priority.capitalize()}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🐾 No tasks yet — add one above!")

    st.divider()
    st.markdown('<div class="section-title">📅 Today\'s Schedule</div>', unsafe_allow_html=True)

    if st.button("🌸 Generate Schedule", use_container_width=True):
        scheduler = Scheduler(st.session_state.owner)
        schedule = scheduler.get_daily_schedule()
        if schedule:
            for t in schedule:
                pet_owner = next(
                    (p.name for p in st.session_state.owner.pets if t in p.tasks), "?")
                emoji = priority_emoji.get(t.priority, "")
                status = "✅ Complete" if t.is_complete else "🔘 Pending"
                st.markdown(f"""
                <div class="task-card">
                    <div class="task-title">{emoji} {t.description}
                        <span style="float:right;font-size:0.9rem;color:#e683b0;">🐾 {pet_owner}</span>
                    </div>
                    <div class="task-meta">🕐 {t.time} &nbsp;|&nbsp; ⏱ {t.duration} min &nbsp;|&nbsp; 🔁 {t.frequency.capitalize()}</div>
                    <div class="task-status">{status} &nbsp;|&nbsp; Priority: {t.priority.capitalize()}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🐾 No tasks scheduled yet!")

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.markdown('<div class="section-title">⚠️ Conflicts Detected</div>', unsafe_allow_html=True)
            for warning in conflicts:
                st.markdown(f'<div class="conflict-box">⚠️ {warning}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 2 — AI Care Advice (RAG)
# ═══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🤖 AI-Powered Care Advice</div>', unsafe_allow_html=True)
    st.write("Select a pet and a focus area. PawPal+ will search its knowledge base and generate personalised tips! 🌸")

    # Pet selector
    pet_names = [p.name for p in st.session_state.owner.pets]
    if not pet_names:
        st.warning("Please add a pet in the Task Planner tab first.")
    else:
        selected_pet_name = st.selectbox("🐾 Choose a pet", pet_names)
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)

        # Pet age (editable here for RAG context)
        pet_age = st.number_input("🎂 Pet age (years)", min_value=0, max_value=30,
                                   value=getattr(selected_pet, "age", 1))
        selected_pet.age = pet_age

        # Focus area
        focus = st.selectbox(
            "🔍 What would you like advice on?",
            ["general", "feeding", "exercise", "grooming", "health", "enrichment"],
            format_func=lambda x: {
                "general": "🌟 General care",
                "feeding": "🍖 Feeding",
                "exercise": "🏃 Exercise",
                "grooming": "✂️ Grooming",
                "health": "💊 Health",
                "enrichment": "🧩 Enrichment",
            }[x]
        )

        # Confidence preview
        existing_task_descs = [t.description for t in selected_pet.tasks]
        confidence = estimate_confidence(selected_pet.species, focus, existing_task_descs)
        st.markdown("**📊 Confidence score** (based on available data before AI call):")
        st.progress(confidence)
        st.caption(f"Score: {confidence:.0%} — {'High ✅' if confidence >= 0.9 else 'Medium 🟡' if confidence >= 0.6 else 'Low ⚠️'}")

        if st.button("✨ Get AI Advice", use_container_width=True):
            with st.spinner("🌸 PawPal+ is thinking..."):
                advice = generate_advice(
                    pet_name=selected_pet.name,
                    species=selected_pet.species,
                    age=pet_age,
                    existing_tasks=existing_task_descs,
                    focus=focus,
                )
            st.markdown('<div class="section-title">💡 PawPal+ Advice</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="advice-box">{advice}</div>', unsafe_allow_html=True)

            # Show what was retrieved
            with st.expander("📚 View retrieved knowledge (RAG context)"):
                from rag_engine import retrieve
                keyword_map = {
                    "feeding":    ["FEEDING"],
                    "exercise":   ["EXERCISE"],
                    "grooming":   ["GROOMING"],
                    "health":     ["HEALTH"],
                    "enrichment": ["ENRICHMENT"],
                    "general":    None,
                }
                raw = retrieve(selected_pet.species, keyword_map.get(focus))
                st.markdown(f'<p style="color:#880e4f;white-space:pre-wrap;font-family:monospace;font-size:0.85rem">{raw}</p>', unsafe_allow_html=True)