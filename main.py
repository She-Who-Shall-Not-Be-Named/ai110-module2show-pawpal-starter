from datetime import datetime
from pawpal_system import Activity, Pet, Owner, Scheduler

# --- Create Owner ---
owner = Owner(name="Alicia")

# --- Create Pets ---
mochi = Pet.create_pet(type="cat", breed="Siamese", name="Mochi")
rex   = Pet.create_pet(type="dog", breed="Labrador", name="Rex")

# --- Create Tasks ---
today = datetime.today()

# Mochi's tasks
mochi.add_task(Activity(
    task="Feed Mochi",
    priority=3,
    time=today.replace(hour=8, minute=0),
    frequency="daily"
))
mochi.add_task(Activity(
    task="Clean litter box",
    priority=2,
    time=today.replace(hour=10, minute=30),
    frequency="daily"
))

# Rex's tasks
rex.add_task(Activity(
    task="Morning walk",
    priority=3,
    time=today.replace(hour=7, minute=0),
    frequency="daily"
))
rex.add_task(Activity(
    task="Vet appointment",
    priority=3,
    time=today.replace(hour=14, minute=0),
    frequency="once"
))
rex.add_task(Activity(
    task="Evening walk",
    priority=2,
    time=today.replace(hour=18, minute=0),
    frequency="daily"
))

# --- Register Pets with Owner ---
owner.set_pet(mochi)
owner.set_pet(rex)

# --- Run Scheduler ---
scheduler = Scheduler(owner)
schedule  = scheduler.get_todays_schedule()

# --- Print Today's Schedule ---
priority_label = {1: "Low", 2: "Medium", 3: "High"}

print(f"\n{'='*40}")
print(f"  PawPal+ | Today's Schedule for {owner.name}")
print(f"{'='*40}")

if not schedule:
    print("  No tasks scheduled for today.")
else:
    for activity in schedule:
        pet_name  = activity.pet.name if activity.pet else "Unknown"
        time_str  = activity.get_time().strftime("%I:%M %p")
        priority  = priority_label[activity.get_priority()]
        print(f"  {time_str}  |  [{priority}]  {activity.task}  ({pet_name})")

print(f"{'='*40}\n")
