# PawPal+ Project Reflection

## 1. System Design
Users should be able to do the following:
    add a pet 
    select/determine specific types of tasks owner wants the ap tp help with 
    schedule tasks in a calander 

**a. Initial design**

- Briefly describe your initial UML design.
- Initil design should include:
Owner class:
    self.name - name of owner
    self.num_pets_owned - how many pets do they own? 
    self.pet_name - names of pet(s) 

    def set_pet()
    def get_pet()
    def remove_pet()
    def set_task()
    def get_task()
    def remove_task()
Pet class:
    self.type - ct, dog, bird , ect?
    self.breed_type - breed of type
    self.name - name of pet

    def create_pet(self, type, breed, name)
Activity class :
    self.task - types of tasks owner wants to track
    self.priority - priority if tasks within a day 
    self.time - time for scheduling 

    def set_priority()
    def get_priority()
    def set_time
    def get_time()

- What classes did you include, and what responsibilities did you assign to each?

- 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
yes, create_pet was converted to a @classmethod since constructing a Pet from an instance made no sense. Activity gained an optional pet: Pet field to capture which pet a task belongs to, closing the missing link between the two classes. time was changed from str to datetime so scheduling logic can actually compare and sort times without string-parsing bugs. On Owner, the pet_name: List[str] was removed since _pets already holds Pet objects with a .name attribute. Finally, num_pets_owned was replaced with a @property that returns len(self._pets) so the count always stays accurate automatically.

Activity gets frequency and completed fields with full method implementations including mark_complete(). Pet takes ownership of its own task list, and Owner drops its flat _tasks list — instead aggregating tasks across all pets via get_all_tasks(). A new Scheduler class acts as the brain, taking an Owner and providing sort, filter, and daily-view logic so that scheduling behavior stays out of both the data classes and the UI.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The scheduler compares task **start times only** — it has no concept of how long a task takes. Two tasks scheduled 20 minutes apart are treated as non-conflicting even if, say, a vet appointment lasts 90 minutes and overlaps everything scheduled after it.

This is a reasonable tradeoff for a pet care app at this stage because:
- Most household pet tasks (feeding, brushing, medication) are short and point-in-time by nature
- Adding a `duration` field to every `Activity` would require owners to estimate times they rarely think about, adding friction to the UI
- The `window_minutes` parameter in `get_conflicts()` partially compensates — setting a window of 60 or 90 minutes catches likely overlaps without needing true duration data

The cost is that a long task like a vet visit won't automatically block the surrounding time slots. A future iteration could add an optional `duration_minutes` field to `Activity` that defaults to `0`, making duration-aware conflict detection opt-in rather than required.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
