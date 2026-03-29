from datetime import datetime
from pawpal_system import Activity, Pet, Owner, Scheduler

owner = Owner(name="Alicia")
mochi = Pet.create_pet(type="cat", breed="Siamese",  name="Mochi")
rex   = Pet.create_pet(type="dog", breed="Labrador", name="Rex")

today = datetime.today()

# Rex — two tasks at the exact same time (same-pet conflict)
w1 = rex.add_task(Activity("Morning walk",  3, today.replace(hour=7, minute=0), "daily"))
w2 = rex.add_task(Activity("Feed Rex",      2, today.replace(hour=7, minute=0), "daily"))

# Mochi — task 10 minutes after another (within 15-min window)
w3 = mochi.add_task(Activity("Feed Mochi",       3, today.replace(hour=8, minute=0),  "daily"))
w4 = mochi.add_task(Activity("Give medication",  3, today.replace(hour=8, minute=10), "daily"))

# Normal tasks — no conflict
rex.add_task(Activity("Vet appointment", 3, today.replace(hour=15, minute=15), "once"))
rex.add_task(Activity("Evening walk",    2, today.replace(hour=18, minute=0),  "daily"))
mochi.add_task(Activity("Clean litter box", 2, today.replace(hour=14, minute=0), "daily"))

owner.set_pet(rex)
owner.set_pet(mochi)

scheduler = Scheduler(owner)

def section(title):
    print(f"\n{'='*54}")
    print(f"  {title}")
    print(f"{'='*54}")

# ── Warnings returned by add_task ────────────────────────────────────────────
section("Warnings returned at add_task time (no crash)")
for label, w in [("Rex: Morning walk", w1), ("Rex: Feed Rex", w2),
                 ("Mochi: Feed Mochi", w3), ("Mochi: Give medication", w4)]:
    result = f'"{w}"' if w and w != "duplicate" else (w or "added OK")
    print(f"  {label:30s} → {result}")

# ── Scheduler conflict warnings — same-pet (default) ────────────────────────
section("Scheduler.get_conflict_warnings() — same-pet only")
warnings = scheduler.get_conflict_warnings(window_minutes=15)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts found.")

# ── Scheduler conflict warnings — all pets, wider window ────────────────────
section("Scheduler.get_conflict_warnings() — all pets, 30-min window")
warnings = scheduler.get_conflict_warnings(window_minutes=30, same_pet_only=False)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts found.")

print(f"\n{'='*54}\n")
print("Program completed without crashing.")
