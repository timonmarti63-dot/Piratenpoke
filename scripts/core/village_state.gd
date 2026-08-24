extends Node
## VillageState — welche Dörfer sind befreit? (Autoload).
##
## Persistiert über Szenenwechsel. Ein Dorf gilt als sicher (`is_safe = true`),
## sobald sein Truppenführer (leader_id) besiegt wurde.
##
## Dörfer beim Start-Setup mit `register_village(id, leader_id)` anmelden;
## danach kann jede Village-Szene `is_safe(id)` abfragen und ihr UI/NPCs
## entsprechend arrangieren.

signal village_liberated(village_id: StringName)

## village_id -> leader_id (StringName)
var _leaders: Dictionary = {}
## Set von befreiten village_ids
var _liberated: Dictionary = {}

func register_village(village_id: StringName, leader_id: StringName) -> void:
	_leaders[village_id] = leader_id

func is_safe(village_id: StringName) -> bool:
	return _liberated.get(village_id, false)

func mark_leader_defeated(leader_id: StringName) -> void:
	for vid in _leaders.keys():
		if _leaders[vid] == leader_id and not _liberated.get(vid, false):
			_liberated[vid] = true
			village_liberated.emit(vid)
