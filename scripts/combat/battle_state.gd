class_name BattleState extends RefCounted
## BattleState — Laufzeit-Zustand eines Kampfes.
##
## Design: kein Node, keine Rendering-Logik. Der BattleController (Scene)
## bekommt eine BattleState-Instanz übergeben und ruft Methoden auf; nach
## jedem Zug feuert BattleState Signale, die die UI konsumiert. Damit ist
## das Kampfmodell reines Datenverhalten und leicht testbar.
##
## Runden-Ablauf:
##   1. Beide Seiten wählen eine Aktion (Player über UI, Enemy über KI).
##   2. Reihenfolge nach `speed` (höher zuerst; Gleichstand → Player zuerst).
##   3. Aktionen sequentiell auflösen. Wenn ein Kämpfer nach Aktion 1 auf 0 HP,
##      wird Aktion 2 übersprungen.
##   4. End-of-Turn-Effekte: Gift-Tick, Buff-Dauer -1.
##   5. Sieger-Check → outcome_changed feuern.

signal hp_changed(who: StringName, current_hp: int, max_hp: int)
signal log_appended(line: String)
signal turn_started(actor: StringName)      ## "player" | "enemy"
signal outcome_changed(outcome: StringName) ## "ongoing" | "player_win" | "enemy_win" | "player_fled"

## Runtime-Sicht auf einen Kämpfer. Enthält Referenz auf die statischen
## Daten + veränderliche Kampfwerte.
class Combatant:
	var data: CombatantData
	var current_hp: int
	var def_bonus: int = 0          ## Additiver Buff aus "def_buff"
	var def_bonus_turns: int = 0
	var poison_dmg: int = 0
	var poison_turns: int = 0

	func _init(d: CombatantData) -> void:
		data = d
		current_hp = d.max_hp

	func is_alive() -> bool: return current_hp > 0
	func effective_defense() -> int: return data.base_defense + def_bonus

var player: Combatant
var enemy: Combatant
var outcome: StringName = &"ongoing"

func _init(player_data: CombatantData, enemy_data_: CombatantData) -> void:
	player = Combatant.new(player_data)
	enemy = Combatant.new(enemy_data_)

## Kann geflohen werden? Bosse verhindern Flucht.
func can_flee() -> bool:
	if enemy.data is EnemyData:
		return not (enemy.data as EnemyData).is_boss
	return true

## Führt eine komplette Runde aus.
## `player_action`: {"type": "skill", "skill": Skill} | {"type": "flee"}
func execute_turn(player_action: Dictionary) -> void:
	if outcome != &"ongoing":
		return

	# Fluchtversuch — sofort, kein Enemy-Zug wenn erfolgreich.
	if player_action.get("type") == "flee":
		if not can_flee():
			log_appended.emit("Flucht nicht möglich!")
		else:
			# Fluchtchance: 0.5 + (player.speed - enemy.speed) * 0.02, geclampt.
			var chance: float = clamp(0.5 + (player.data.speed - enemy.data.speed) * 0.02, 0.1, 0.95)
			if randf() < chance:
				log_appended.emit("Du bist erfolgreich geflohen!")
				outcome = &"player_fled"
				outcome_changed.emit(outcome)
				return
			log_appended.emit("Flucht misslungen!")
		# Nach fehlgeschlagener Flucht darf der Gegner ziehen.
		_enemy_turn()
		_end_of_turn()
		_check_outcome()
		return

	# Skill-Runde: Reihenfolge nach Speed.
	var player_first: bool = player.data.speed >= enemy.data.speed
	turn_started.emit(&"player" if player_first else &"enemy")

	if player_first:
		_resolve_skill(player, enemy, player_action.get("skill"))
		if enemy.is_alive():
			_enemy_turn()
	else:
		_enemy_turn()
		if player.is_alive():
			_resolve_skill(player, enemy, player_action.get("skill"))

	_end_of_turn()
	_check_outcome()

func _enemy_turn() -> void:
	var skill: Skill = _pick_enemy_skill()
	if skill == null:
		log_appended.emit("%s ist ratlos." % enemy.data.display_name)
		return
	_resolve_skill(enemy, player, skill)

func _pick_enemy_skill() -> Skill:
	if enemy.data.skills.is_empty():
		return null
	var profile: StringName = &"random"
	if enemy.data is EnemyData:
		profile = (enemy.data as EnemyData).ai_profile
	if profile == &"aggressive":
		for s in enemy.data.skills:
			if s is Skill and s.effect == &"damage":
				return s
	# Fallback / "random"
	var candidates: Array = []
	for s in enemy.data.skills:
		if s is Skill:
			candidates.append(s)
	if candidates.is_empty():
		return null
	return candidates[randi() % candidates.size()]

func _resolve_skill(actor: Combatant, target: Combatant, skill: Skill) -> void:
	if skill == null or not actor.is_alive():
		return

	# Trefferwurf
	if randf() > skill.accuracy:
		log_appended.emit("%s setzt %s ein — daneben!" % [actor.data.display_name, skill.display_name])
		return

	match skill.effect:
		&"damage":
			var mult: float = TypeChart.multiplier(skill.element, target.data.element)
			var dmg: int = DamageCalc.compute(
				actor.data.base_attack,
				target.effective_defense(),
				skill.power,
				mult
			)
			target.current_hp = max(0, target.current_hp - dmg)
			var line := "%s setzt %s ein und macht %d Schaden." % [
				actor.data.display_name, skill.display_name, dmg
			]
			var extra := TypeChart.describe(mult)
			if extra != "":
				line += " %s" % extra
			log_appended.emit(line)
			_emit_hp(target)

		&"heal":
			var healed: int = min(skill.power, actor.data.max_hp - actor.current_hp)
			actor.current_hp += healed
			log_appended.emit("%s heilt sich um %d HP." % [actor.data.display_name, healed])
			_emit_hp(actor)

		&"poison":
			target.poison_dmg = max(target.poison_dmg, skill.power)
			target.poison_turns = max(target.poison_turns, skill.duration)
			log_appended.emit("%s wird vergiftet!" % target.data.display_name)

		&"def_buff":
			actor.def_bonus += skill.power
			actor.def_bonus_turns = max(actor.def_bonus_turns, skill.duration)
			log_appended.emit("%s stärkt seine Verteidigung." % actor.data.display_name)

		_:
			log_appended.emit("%s setzt %s ein." % [actor.data.display_name, skill.display_name])

func _end_of_turn() -> void:
	for c in [player, enemy]:
		if c.poison_turns > 0 and c.is_alive():
			c.current_hp = max(0, c.current_hp - c.poison_dmg)
			log_appended.emit("%s erleidet %d Gift-Schaden." % [c.data.display_name, c.poison_dmg])
			c.poison_turns -= 1
			_emit_hp(c)
		if c.def_bonus_turns > 0:
			c.def_bonus_turns -= 1
			if c.def_bonus_turns == 0:
				c.def_bonus = 0

func _check_outcome() -> void:
	if not player.is_alive():
		outcome = &"enemy_win"
		outcome_changed.emit(outcome)
	elif not enemy.is_alive():
		outcome = &"player_win"
		outcome_changed.emit(outcome)

func _emit_hp(c: Combatant) -> void:
	var who: StringName = &"player" if c == player else &"enemy"
	hp_changed.emit(who, c.current_hp, c.data.max_hp)
