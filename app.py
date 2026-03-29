import streamlit as st
from datetime import datetime
from pawpal_system import Activity, Pet, Owner, Scheduler

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ─── Session state bootstrap ────────────────────────────────────────────────
if "owner" not in st.session_state:
    owner = Owner(name="Alicia")
    mochi = Pet.create_pet(type="cat", breed="Siamese",  name="Mochi")
    rex   = Pet.create_pet(type="dog", breed="Labrador", name="Rex")
    today = datetime.today()
    mochi.add_task(Activity("Feed Mochi",       3, today.replace(hour=8,  minute=0),  "daily"))
    mochi.add_task(Activity("Clean litter box", 2, today.replace(hour=14, minute=50), "daily"))
    rex.add_task(Activity("Morning walk",        3, today.replace(hour=7,  minute=0),  "daily"))
    rex.add_task(Activity("Vet appointment",     3, today.replace(hour=15, minute=15), "once"))
    rex.add_task(Activity("Evening walk",        2, today.replace(hour=18, minute=0),  "daily"))
    owner.set_pet(mochi)
    owner.set_pet(rex)
    st.session_state.owner = owner

owner     = st.session_state.owner
scheduler = Scheduler(owner)

PRIORITY_LABEL = {1: "🟢 Low", 2: "🟡 Medium", 3: "🔴 High"}
PRIORITY_INT   = {"High": 3, "Medium": 2, "Low": 1}

# ─── Header ─────────────────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption(f"Today is **{datetime.today().strftime('%A, %B %d %Y')}**  •  Owner: **{owner.name}**")
st.divider()

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Add pet / Add task / Recurring rollover
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("Manage")

    # ── Add a new pet ────────────────────────────────────────────────────────
    with st.expander("➕ Add Pet"):
        with st.form("add_pet_form"):
            p_name  = st.text_input("Name")
            p_type  = st.selectbox("Type", ["dog", "cat", "bird", "rabbit", "other"])
            p_breed = st.text_input("Breed")
            if st.form_submit_button("Add Pet"):
                if p_name.strip():
                    new_pet = Pet.create_pet(type=p_type, breed=p_breed, name=p_name.strip())
                    owner.set_pet(new_pet)
                    st.toast(f"{p_name.strip()} added!", icon="✅")
                    st.rerun()
                else:
                    st.error("Pet name is required.")

    # ── Add a new task ───────────────────────────────────────────────────────
    with st.expander("➕ Add Task", expanded=True):
        pet_names = [p.name for p in owner.get_pet()]
        if not pet_names:
            st.info("Add a pet first.")
        else:
            with st.form("add_task_form"):
                t_pet      = st.selectbox("Pet", pet_names)
                t_task     = st.text_input("Task name")
                t_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                t_time     = st.time_input("Time", value=datetime.now().replace(minute=0, second=0, microsecond=0))
                t_freq     = st.selectbox("Frequency", ["daily", "weekly", "monthly", "once"])

                if st.form_submit_button("Add Task"):
                    if t_task.strip():
                        pet = next(p for p in owner.get_pet() if p.name == t_pet)
                        scheduled = datetime.today().replace(
                            hour=t_time.hour, minute=t_time.minute, second=0, microsecond=0
                        )
                        new_act = Activity(
                            task=t_task.strip(),
                            priority=PRIORITY_INT[t_priority],
                            time=scheduled,
                            frequency=t_freq,
                        )
                        try:
                            added = pet.add_task(new_act)
                            if added:
                                st.toast(f"Task added for {t_pet}!", icon="✅")
                            else:
                                st.toast("Duplicate — task already exists at that time.", icon="⚠️")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"Scheduling conflict: {e}")
                    else:
                        st.error("Task name is required.")

    st.divider()

    # ── Recurring rollover ───────────────────────────────────────────────────
    st.subheader("Recurring Tasks")
    next_tasks = scheduler.generate_next_occurrences()
    st.caption(f"{len(next_tasks)} recurring task(s) ready to roll over tomorrow.")
    if st.button("Generate Tomorrow's Tasks"):
        added_count = 0
        for nt in next_tasks:
            for orig in owner.get_all_tasks():
                if orig.task == nt.task and orig.frequency == nt.frequency and orig.pet:
                    try:
                        orig.pet.add_task(nt)
                        added_count += 1
                    except ValueError:
                        pass
                    break
        st.toast(f"Added {added_count} task(s) for tomorrow!", icon="🔁")
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# FILTERS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("**Filters**")
col1, col2, col3 = st.columns(3)

with col1:
    filter_pet = st.selectbox("Pet", ["All pets"] + [p.name for p in owner.get_pet()])

with col2:
    filter_status = st.selectbox("Status", ["Pending", "Completed", "All"])

with col3:
    sort_by = st.selectbox("Sort by", ["Urgency (smart)", "Time", "Priority"])

st.divider()

# ─── Build filtered + sorted schedule ───────────────────────────────────────
def build_schedule():
    pet_name  = None if filter_pet == "All pets" else filter_pet
    completed = {"Pending": False, "Completed": True}.get(filter_status)

    tasks = [
        t for t in scheduler.filter_tasks(pet_name=pet_name, completed=completed)
        if t.is_due_today()
    ]

    if sort_by == "Urgency (smart)":
        tasks = sorted(tasks, key=lambda t: (-t.urgency_score(), t.time))
    elif sort_by == "Time":
        tasks = sorted(tasks, key=lambda t: t.time)
    elif sort_by == "Priority":
        tasks = sorted(tasks, key=lambda t: (-t.priority, t.time))

    return tasks

tasks    = build_schedule()
overdue  = scheduler.get_overdue_tasks()
upcoming = scheduler.get_upcoming_tasks(hours=2)

# ─── Alert banners (hidden when browsing completed tasks) ────────────────────
if filter_status != "Completed":
    visible_overdue = [
        t for t in overdue
        if filter_pet == "All pets" or (t.pet and t.pet.name == filter_pet)
    ]
    visible_upcoming = [
        t for t in upcoming
        if filter_pet == "All pets" or (t.pet and t.pet.name == filter_pet)
    ]

    if visible_overdue:
        names = ", ".join(t.task for t in visible_overdue)
        st.error(f"⚠️ **{len(visible_overdue)} overdue:** {names}")

    if visible_upcoming:
        names = ", ".join(
            f"{t.task} at {t.get_time().strftime('%I:%M %p')}" for t in visible_upcoming
        )
        st.warning(f"⏰ **Coming up soon:** {names}")

# ─── Task table ──────────────────────────────────────────────────────────────
filter_label = "" if filter_status == "All" else f"{filter_status} · "
pet_label    = "" if filter_pet == "All pets" else f"{filter_pet} · "
st.subheader(f"Schedule — {pet_label}{filter_label}{len(tasks)} task(s)")

if not tasks:
    st.info("No tasks match the current filters.")
else:
    col_widths = [1.2, 2.8, 1.4, 1.6, 1.4, 1.2]
    hdr = st.columns(col_widths)
    for col, label in zip(hdr, ["**Time**", "**Task**", "**Pet**", "**Priority**", "**Status**", "**Action**"]):
        col.markdown(label)
    st.divider()

    for i, task in enumerate(tasks):
        row      = st.columns(col_widths)
        pet_name = task.pet.name if task.pet else "—"
        flag     = " 📌" if task.is_one_time_high_priority() else ""
        is_late  = task in overdue

        if task.completed:
            status = "✅ Done"
        elif is_late:
            status = "🔴 Overdue"
        elif task in upcoming:
            status = "⏰ Soon"
        else:
            status = "⏳ Pending"

        row[0].write(task.get_time().strftime("%I:%M %p"))
        row[1].write(f"{task.task}{flag}")
        row[2].write(pet_name)
        row[3].write(PRIORITY_LABEL[task.get_priority()])
        row[4].write(status)

        btn_label = "Undo" if task.completed else "Mark done"
        if row[5].button(btn_label, key=f"btn_{i}_{id(task)}"):
            if task.completed:
                task.completed = False
            else:
                task.mark_complete()
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# PER-PET SUMMARY
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Summary by Pet")

summary = scheduler.get_summary_by_pet()
if not summary:
    st.success("All tasks complete for today! 🎉")
else:
    cols = st.columns(max(len(summary), 1))
    for col, (pet_name, pet_tasks) in zip(cols, summary.items()):
        with col:
            st.markdown(f"**{pet_name}** — {len(pet_tasks)} pending")
            for t in pet_tasks:
                flag = " 📌" if t.is_one_time_high_priority() else ""
                st.markdown(f"- `{t.get_time().strftime('%I:%M %p')}` {PRIORITY_LABEL[t.get_priority()]} {t.task}{flag}")
