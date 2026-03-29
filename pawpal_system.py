from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    type: str
    breed_type: str
    name: str

    def create_pet(self, type: str, breed: str, name: str) -> "Pet":
        pass


@dataclass
class Activity:
    task: str
    priority: int
    time: str

    def set_priority(self, priority: int) -> None:
        pass

    def get_priority(self) -> int:
        pass

    def set_time(self, time: str) -> None:
        pass

    def get_time(self) -> str:
        pass


@dataclass
class Owner:
    name: str
    num_pets_owned: int = 0
    pet_name: List[str] = field(default_factory=list)
    _pets: List[Pet] = field(default_factory=list)
    _tasks: List[Activity] = field(default_factory=list)

    def set_pet(self, pet: Pet) -> None:
        pass

    def get_pet(self) -> List[Pet]:
        pass

    def set_task(self, activity: Activity) -> None:
        pass

    def get_task(self) -> List[Activity]:
        pass
