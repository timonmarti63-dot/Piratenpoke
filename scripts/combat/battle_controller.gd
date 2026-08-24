extends Control
## BattleController — Combat-Scene-Root.
##
## Bindet BattleState an die UI. Alle vier Menüs (Kämpfen/Item/Wechseln/Flucht)
## sind jetzt funktional.
##
## Aufruf-Vertrag:
##   SceneRouter.push_battle(...) instanziiert diese Szene und ruft
##   `start(party, active_index, enemy_data)` auf.

@onready var enemy_name_label: Label = %EnemyName
@onready var enemy_hp_bar: ProgressBar = %EnemyHP
@onready var enemy_hp_label: Label = %EnemyHPLabel

@onready var player_name_label: Label = %PlayerName
@onready var player_hp_bar: ProgressBar = %PlayerHP
@onready var player_hp_label: Label = %PlayerHPLabel

@onready var log_label: RichTextLabel = %Log

@onready var main_menu: Container = %MainMenu
@onready var skill_menu: Container = %SkillMenu
@onready var item_menu: Container = %ItemMenu
@onready var switch_menu: Container = %SwitchMenu

@onready var btn_fight: Button = %BtnFight
@onready var btn_item: Button = %BtnItem
@onready var btn_switch: Button = %BtnSwitch
@onready var btn_flee: Button = %BtnFlee

@onready var skill_buttons: Container = %SkillButtons
@onready var item_buttons: Container = %ItemButtons
@onready var switch_buttons: Container = %SwitchButtons

var _state: BattleState
var _input_locked: bool = false

func _ready() -> void:
	btn_fight.pressed.connect(func(): _show(skill_menu))
	btn_item.pressed.connect(_open_item_menu)
	btn_switch.pressed.connect(_open_switch_menu)
	btn_flee.pressed.connect(_on_flee_pressed)
	%BtnSkillBack.pressed.connect(_show_main)
	%BtnItemBack.pressed.connect(_show_main)
	%BtnSwitchBack.pressed.connect(_show_main)

func start(party: Array, active_index: int, enemy_data_: CombatantData) -> void:
	_state = BattleState.new(party, enemy_data_, active_index)
	_state.hp_changed.connect(_on_hp_changed)
	_state.log_appended.connect(_append_log)
	_state.outcome_changed.connect(_on_outcome_changed)
	_state.party_changed.connect(_refresh_player_ui)

	enemy_name_label.text = enemy_data_.display_name
	_refresh_player_ui()
	_refresh_hp(_state.enemy, true)

	btn_flee.disabled = not _state.can_flee()

	_append_log("Ein wilder %s taucht auf!" % enemy_data_.display_name)
	_build_skill_buttons()
	_show_main()

# --- Menü-Aufbau ------------------------------------------------------

func _refresh_player_ui() -> void:
	var p := _state.player()
	player_name_label.text = p.data.display_name
	_refresh_hp(p, false)
	_build_skill_buttons()

func _build_skill_buttons() -> void:
	for child in skill_buttons.get_children():
		child.queue_free()
	var pdata: CombatantData = _state.player().data
	var count: int = min(4, pdata.skills.size())
	for i in count:
		var s: Skill = pdata.skills[i] as Skill
		if s == null:
			continue
		var b := Button.new()
		b.text = "%s  (%s, Pow %d)" % [s.display_name, String(s.element).capitalize(), s.power]
		b.tooltip_text = s.description
		b.pressed.connect(_on_skill_chosen.bind(s))
		skill_buttons.add_child(b)

func _open_item_menu() -> void:
	for child in item_buttons.get_children():
		child.queue_free()
	var consumables: Array = Inventory.consumables()
	if consumables.is_empty():
		var lbl := Label.new()
		lbl.text = "Keine Items im Beutel."
		item_buttons.add_child(lbl)
	else:
		for it in consumables:
			var c: Consumable = it
			if not c.usable_in_combat:
				continue
			var b := Button.new()
			var n: int = Inventory.count_of(c)
			b.text = "%s  x%d" % [c.display_name, n]
			b.tooltip_text = c.description
			b.pressed.connect(_on_item_chosen.bind(c))
			item_buttons.add_child(b)
	_show(item_menu)

func _open_switch_menu() -> void:
	for child in switch_buttons.get_children():
		child.queue_free()
	if _state.party.size() <= 1:
		var lbl := Label.new()
		lbl.text = "Keine weiteren Crew-Mitglieder dabei."
		switch_buttons.add_child(lbl)
	else:
		for i in range(_state.party.size()):
			var c = _state.party[i]
			var b := Button.new()
			var status: String = " (KO)" if not c.is_alive() else ""
			var mark: String = " ←" if i == _state.active_player_index else ""
			b.text = "%s  HP %d/%d%s%s" % [c.data.display_name, c.current_hp, c.data.max_hp, status, mark]
			b.disabled = (i == _state.active_player_index) or (not c.is_alive())
			b.pressed.connect(_on_switch_chosen.bind(i))
			switch_buttons.add_child(b)
	_show(switch_menu)

func _show(container: Container) -> void:
	main_menu.visible = (container == main_menu)
	skill_menu.visible = (container == skill_menu)
	item_menu.visible = (container == item_menu)
	switch_menu.visible = (container == switch_menu)

func _show_main() -> void: _show(main_menu)

# --- Aktions-Handler --------------------------------------------------

func _on_skill_chosen(skill: Skill) -> void:
	if _input_locked: return
	_lock_and_execute({"type": "skill", "skill": skill})

func _on_item_chosen(item: Consumable) -> void:
	if _input_locked: return
	_lock_and_execute({"type": "item", "item": item})

func _on_switch_chosen(index: int) -> void:
	if _input_locked: return
	_lock_and_execute({"type": "switch", "index": index})

func _on_flee_pressed() -> void:
	if _input_locked: return
	_lock_and_execute({"type": "flee"})

func _lock_and_execute(action: Dictionary) -> void:
	_input_locked = true
	_show_main()
	_state.execute_turn(action)
	await get_tree().create_timer(0.9).timeout
	_input_locked = false

# --- HP-UI ------------------------------------------------------------

func _on_hp_changed(who: StringName, index: int, current: int, maximum: int) -> void:
	if who == &"enemy":
		_set_bar(enemy_hp_bar, enemy_hp_label, current, maximum)
	elif index == _state.active_player_index:
		_set_bar(player_hp_bar, player_hp_label, current, maximum)

func _refresh_hp(c: BattleState.Combatant, is_enemy: bool) -> void:
	if is_enemy:
		_set_bar(enemy_hp_bar, enemy_hp_label, c.current_hp, c.data.max_hp)
	else:
		_set_bar(player_hp_bar, player_hp_label, c.current_hp, c.data.max_hp)

func _set_bar(bar: ProgressBar, label: Label, cur: int, mx: int) -> void:
	bar.max_value = mx
	bar.value = cur
	label.text = "%d / %d" % [cur, mx]

func _append_log(line: String) -> void:
	log_label.append_text(line + "\n")

func _on_outcome_changed(outcome: StringName) -> void:
	await get_tree().create_timer(0.8).timeout
	match outcome:
		&"player_win":
			_append_log("[b]Sieg![/b]")
			if _state.enemy.data is EnemyData:
				var e := _state.enemy.data as EnemyData
				_append_log("+%d XP, +%d Gold." % [e.xp_reward, e.gold_reward])
				Inventory.add_gold(e.gold_reward)
				# XP kommt in v0.6 mit dem Fortschritts-System.
		&"enemy_win":
			_append_log("[b]Deine Crew wurde besiegt…[/b]")
		&"player_fled":
			pass
	await get_tree().create_timer(1.2).timeout
	SceneRouter.finish_battle(outcome)
