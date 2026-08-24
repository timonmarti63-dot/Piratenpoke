class_name Armor extends Item
## Armor — dauerhafte Rüstung, wird 1 Crew-Mitglied zugewiesen.

@export var defense_bonus: int = 4
@export var allowed_elements: Array = []

func can_be_equipped_by(crew: CrewMember) -> bool:
	if allowed_elements.is_empty():
		return true
	return crew.element in allowed_elements
