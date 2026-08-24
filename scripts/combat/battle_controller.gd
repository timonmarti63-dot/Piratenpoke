extends Control
## BattleController — Combat-Scene-Root.
##
## Bindet BattleState an das UI:
##   - Namen + HP-Bars oben (Gegner) und unten (Spieler-Crew-Aktiv).
##   - Log-Panel darunter zeigt die letzten Zeilen der Runde.
##   - 4-Buttons-Menü: Kämpfen / Item / Wechseln / Flucht.
##       * Kämpfen öffnet Sub-Menü mit bis zu 4 Skills.
##       * Item + Wechseln sind in v0.3 noch Platzhalter (v0.4 mit Inventar).
##
## Der Controller sperrt Input während Log-Sequenzen, damit man Runden nicht
## überspringen kann bevor sie visuell abgespielt sind.

@onready var enemy_name_label: Label = %EnemyName
@onready var enemy_hp_bar: ProgressBar = %EnemyHP
@onready var enemy_hp_label: Label = %EnemyHPLabel

@onready var player_name_label: Label = %PlayerName
@onready var player_hp_bar: ProgressBar = %PlayerHP
@onready var player_hp_label: Label = %PlayerHPLabel

@onready var log_label: RichTextLabel = %Log

@onready var main_menu: Container = %MainMenu
@onready var skill_menu: Container = %SkillMenu
@onready var btn_fight: Button = %BtnFight
@onready var btn_item: Button = %BtnItem
@onready var btn_switch: Button = %BtnSwitch
@onready var btn_flee: Button = %BtnFlee
@onready var btn_back: Button = %BtnBack
@onready var skill_buttons_container: Container = %SkillButtons

var _state: BattleState
var _input_locked: bool = false

func _ready() -> void:
	btn_fight.pressed.connect(_show_skill_menu)
	btn_item.pressed.connect(func(): _append_log("[i]Items kommen in v0.4.[/i]"))
	btn_switch.pressed.connect(func(): _append_log("[i]Wechseln kommt in v0.4.[/i]"))
	btn_flee.pressed.connect(_on_flee_pressed)
	btn_back.pressed.connect(_show_main_menu)
	skill_menu.visible = false

## Wird von SceneRouter.push_battle nach Instantiierung aufgerufen.
func start(player_data: CombatantData, enemy_data_: CombatantData) -> void:
	_state = BattleState.new(player_data, enemy_data_)
	_state.hp_changed.connect(_on_hp_changed)
	_state.log_appended.connect(_append_log)
	_state.outcome_changed.connect(_on_outcome_changed)

	# UI initialisieren.
	enemy_name_label.text = enemy_data_.display_name
	player_name_label.text = player_data.display_name
	_refresh_hp(_state.player, "player")
	_refresh_hp(_state.enemy, "enemy")

	btn_flee.disabled = not _state.can_flee()

	_append_log("Ein wilder %s taucht auf!" % enemy_data_.display_name)
	_build_skill_buttons(player_data)
	_show_main_menu()

func _build_skill_buttons(player_data: CombatantData) -> void:
	for child in skill_buttons_container.get_children():
		child.queue_free()
	var count: int = min(4, player_data.skills.size())
	for i in count:
		var s: Skill = player_data.skills[i] as Skill
		if s == null:
			continue
		var b := Button.new()
		b.text = "%s  (%s, Pow %d)" % [s.display_name, String(s.element).capitalize(), s.power]
		b.tooltip_text = s.description
		b.pressed.connect(_on_skill_chosen.bind(s))
		skill_buttons_container.add_child(b)

func _show_main_menu() -> void:
	main_menu.visible = true
	skill_menu.visible = false

func _show_skill_menu() -> void:
	main_menu.visible = false
	skill_menu.visible = true

func _on_skill_chosen(skill: Skill) -> void:
	if _input_locked:
		return
	_lock_and_execute({"type": "skill", "skill": skill})

func _on_flee_pressed() -> void:
	if _input_locked:
		return
	_lock_and_execute({"type": "flee"})

func _lock_and_execute(action: Dictionary) -> void:
	_input_locked = true
	_show_main_menu()
	_state.execute_turn(action)
	# Kleine Verzögerung, damit User Log-Zeilen lesen kann. Wenn Kampf endet,
	# übernimmt _on_outcome_changed das Schließen.
	await get_tree().create_timer(0.9).timeout
	_input_locked = false

func _on_hp_changed(who: StringName, current: int, maximum: int) -> void:
	if who == &"player":
		_set_bar(player_hp_bar, player_hp_label, current, maximum)
	else:
		_set_bar(enemy_hp_bar, enemy_hp_label, current, maximum)

func _refresh_hp(c: BattleState.Combatant, who: String) -> void:
	if who == "player":
		_set_bar(player_hp_bar, player_hp_label, c.current_hp, c.data.max_hp)
	else:
		_set_bar(enemy_hp_bar, enemy_hp_label, c.current_hp, c.data.max_hp)

func _set_bar(bar: ProgressBar, label: Label, cur: int, mx: int) -> void:
	bar.max_value = mx
	bar.value = cur
	label.text = "%d / %d" % [cur, mx]

func _append_log(line: String) -> void:
	log_label.append_text(line + "\n")

func _on_outcome_changed(outcome: StringName) -> void:
	# Etwas warten, damit die letzte Log-Zeile lesbar ist.
	await get_tree().create_timer(0.8).timeout
	match outcome:
		&"player_win":
			_append_log("[b]Sieg![/b]")
			if _state.enemy.data is EnemyData:
				var e := _state.enemy.data as EnemyData
				_append_log("+%d XP, +%d Gold." % [e.xp_reward, e.gold_reward])
		&"enemy_win":
			_append_log("[b]Deine Crew wurde besiegt…[/b]")
		&"player_fled":
			pass
	await get_tree().create_timer(1.2).timeout
	SceneRouter.finish_battle(outcome)
