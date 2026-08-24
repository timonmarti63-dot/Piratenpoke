class_name Weapon extends Item
## Weapon — dauerhafte Waffe, wird 1 Crew-Mitglied zugewiesen.
##
## Restriktionen (siehe GDD §11): ein Sumpf-Healer darf keine Bergbau-Axt tragen.
## Das lösen wir über `allowed_elements`: leer = alle dürfen, sonst muss das
## `element` des CrewMember in der Liste sein.

@export var attack_bonus: int = 5
## Leer = für alle Elemente. Sonst z. B. [&"fire", &"stone"].
@export var allowed_elements: Array = []

func can_be_equipped_by(crew: CrewMember) -> bool:
	if allowed_elements.is_empty():
		return true
	return crew.element in allowed_elements
