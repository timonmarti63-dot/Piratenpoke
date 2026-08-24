class_name BattleState extends RefCounted
## BattleState — Laufzeit-Zustand eines Kampfes.
##
## Modell: eine Spieler-Partei (Array[Combatant]) mit `active_player_index`,
## und ein einzelner Gegner. Wechseln tauscht den aktiven Player und kostet
## einen ganzen Zug (nur der Gegner handelt).
##
## Item-Anwendung im Kampf: `apply_item(consumable)` — verbraucht 1 aus
## Inventory und wirkt sofort. Kostet einen ganzen Zug wie Wechseln.
##
## Signals:
##   hp_changed(who, index, current, max) — who: "player"|"enemy"
##   log_appended, turn_started
##   outcome_changed("ongoing"|"player_win"|"enemy_win"|"player_fled")
##   party_changed — z.B. wenn aktiver Kämpfer wechselt

signal hp_changed(who: StringName, index: int, current_hp: int, max_hp: int)
signal log_appended(line: String)
signal turn_started(actor: StringName)
signal outcome_changed(outcome: StringName)
signal party_changed

class Combatant:
	var data: CombatantData
	var current_hp: int
	var def_bonus: int = 0
	var def_bonus_turns: int = 0
	var atk_bonus: int = 0
	var atk_bonus_turns: int = 0
	var poison_dmg: int = 0
	var poison_turns: int = 0

	func _init(d: CombatantData) -> void:
		data = d
		current_hp = d.max_hp

	func is_alive() -> bool: return current_hp > 0

	## Effektive Werte (Basis + Gear + Buffs).
	func effective_attack() -> int:
		var gear: int = 0
		if data is CrewMember and (data as CrewMember).weapon != null:
			gear = (data as CrewMember).weapon.attack_bonus
		return data.base_attack + gear + atk_bonus

	func effective_defense() -> int:
		var gear: int = 0
		if data is CrewMember and (data as CrewMember).armor != null:
			gear = (data as CrewMember).armor.defense_bonus
		return data.base_defense + gear + def_bonus

var party: Array = []           ## Array[Combatant]
var active_player_index: int = 0
var enemy: Combatant
var outcome: StringName = &"ongoing"

func _init(party_data: Array, enemy_data_: CombatantData, active_idx: int = 0) -> void:
	for d in party_data:
		if d is CombatantData:
			party.append(Combatant.new(d))
	active_player_index = clamp(active_idx, 0, party.size() - 1)
	enemy = Combatant.new(enemy_data_)

func player() -> Combatant:
	return party[active_player_index]

func can_flee() -> bool:
	if enemy.data is EnemyData:
		return not (enemy.data as EnemyData).is_boss
	return true

func has_reserves_alive() -> bool:
	for c in party:
		if c != player() and c.is_alive():
			return true
	return false

## Führt eine komplette Runde aus.
## Aktionen: {"type":"skill","skill":Skill} | {"type":"flee"}
##          | {"type":"switch","index":int} | {"type":"item","item":Consumable}
func execute_turn(action: Dictionary) -> void:
	if outcome != &"ongoing":
		return

	match action.get("type"):
		"flee":     _handle_flee()
		"switch":   _handle_switch(action.get("index", -1))
		"item":     _handle_item(action.get("item"))
		"skill", _: _handle_skill_round(action.get("skill"))

	_end_of_turn()
	_check_outcome()

# --- Aktions-Handler --------------------------------------------------

func _handle_flee() -> void:
	if not can_flee():
		log_appended.emit("Flucht nicht möglich!")
		_enemy_turn()
		return
	var chance: float = clamp(0.5 + (player().data.speed - enemy.data.speed) * 0.02, 0.1, 0.95)
	if randf() < chance:
		log_appended.emit("Du bist erfolgreich geflohen!")
		outcome = &"player_fled"
		outcome_changed.emit(outcome)
		return
	log_appended.emit("Flucht misslungen!")
	_enemy_turn()

func _handle_switch(new_index: int) -> void:
	if new_index < 0 or new_index >= party.size():
		return
	if new_index == active_player_index:
		return
	if not party[new_index].is_alive():
		log_appended.emit("%s ist kampfunfähig." % party[new_index].data.display_name)
		return
	var old_name := player().data.display_name
	active_player_index = new_index
	log_appended.emit("%s tritt zurück — %s übernimmt!" % [old_name, player().data.display_name])
	party_changed.emit()
	_enemy_turn()

func _handle_item(consumable) -> void:
	if not (consumable is Consumable):
		return
	var c: Consumable = consumable
	if Inventory.count_of(c) <= 0:
		log_appended.emit("Kein %s mehr!" % c.display_name)
		return
	Inventory.remove_item(c, 1)
	_apply_consumable_to(player(), c)
	_enemy_turn()

func _handle_skill_round(skill) -> void:
	if not (skill is Skill):
		return
	var s: Skill = skill
	var player_first: bool = player().data.speed >= enemy.data.speed
	turn_started.emit(&"player" if player_first else &"enemy")
	if player_first:
		_resolve_skill(player(), enemy, s, true)
		if enemy.is_alive():
			_enemy_turn()
	else:
		_enemy_turn()
		if player().is_alive():
			_resolve_skill(player(), enemy, s, true)

func _enemy_turn() -> void:
	if not enemy.is_alive() or not player().is_alive():
		return
	var skill: Skill = _pick_enemy_skill()
	if skill == null:
		log_appended.emit("%s ist ratlos." % enemy.data.display_name)
		return
	_resolve_skill(enemy, player(), skill, false)

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
	var candidates: Array = []
	for s in enemy.data.skills:
		if s is Skill:
			candidates.append(s)
	if candidates.is_empty():
		return null
	return candidates[randi() % candidates.size()]

# --- Effekt-Auflösung -------------------------------------------------

func _resolve_skill(actor: Combatant, target: Combatant, skill: Skill, actor_is_player: bool) -> void:
	if skill == null or not actor.is_alive():
		return
	if randf() > skill.accuracy:
		log_appended.emit("%s setzt %s ein — daneben!" % [actor.data.display_name, skill.display_name])
		return

	match skill.effect:
		&"damage":
			var mult: float = TypeChart.multiplier(skill.element, target.data.element)
			var dmg: int = DamageCalc.compute(
				actor.effective_attack(),
				target.effective_defense(),
				skill.power,
				mult
			)
			target.current_hp = max(0, target.current_hp - dmg)
			var line: String = "%s setzt %s ein und macht %d Schaden." % [
				actor.data.display_name, skill.display_name, dmg
			]
			var extra: String = TypeChart.describe(mult)
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

func _apply_consumable_to(c: Combatant, item: Consumable) -> void:
	match item.effect:
		&"heal":
			var healed: int = min(item.power, c.data.max_hp - c.current_hp)
			c.current_hp += healed
			log_appended.emit("%s heilt %s um %d HP." % [item.display_name, c.data.display_name, healed])
			_emit_hp(c)
		&"cure_poison":
			c.poison_dmg = 0
			c.poison_turns = 0
			log_appended.emit("%s wurde entgiftet." % c.data.display_name)
		&"atk_up":
			c.atk_bonus += item.power
			c.atk_bonus_turns = max(c.atk_bonus_turns, item.duration)
			log_appended.emit("%s fühlt sich stärker!" % c.data.display_name)
		&"def_up":
			c.def_bonus += item.power
			c.def_bonus_turns = max(c.def_bonus_turns, item.duration)
			log_appended.emit("%s' Haut wird härter!" % c.data.display_name)
		_:
			log_appended.emit("%s hat keine Wirkung." % item.display_name)

func _end_of_turn() -> void:
	for c in party + [enemy]:
		if not c.is_alive():
			continue
		if c.poison_turns > 0:
			c.current_hp = max(0, c.current_hp - c.poison_dmg)
			log_appended.emit("%s erleidet %d Gift-Schaden." % [c.data.display_name, c.poison_dmg])
			c.poison_turns -= 1
			_emit_hp(c)
		if c.def_bonus_turns > 0:
			c.def_bonus_turns -= 1
			if c.def_bonus_turns == 0:
				c.def_bonus = 0
		if c.atk_bonus_turns > 0:
			c.atk_bonus_turns -= 1
			if c.atk_bonus_turns == 0:
				c.atk_bonus = 0

func _check_outcome() -> void:
	if not enemy.is_alive():
		outcome = &"player_win"
		outcome_changed.emit(outcome)
		return
	if not player().is_alive():
		# Automatischer Wechsel, wenn Reserven da sind
		if has_reserves_alive():
			log_appended.emit("%s ist kampfunfähig!" % player().data.display_name)
			for i in range(party.size()):
				if party[i].is_alive():
					active_player_index = i
					log_appended.emit("%s springt ein!" % player().data.display_name)
					party_changed.emit()
					return
		outcome = &"enemy_win"
		outcome_changed.emit(outcome)

func _emit_hp(c: Combatant) -> void:
	if c == enemy:
		hp_changed.emit(&"enemy", 0, c.current_hp, c.data.max_hp)
	else:
		var idx: int = party.find(c)
		hp_changed.emit(&"player", idx, c.current_hp, c.data.max_hp)
