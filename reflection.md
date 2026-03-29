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
    def set_task()
    def get_task()
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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
