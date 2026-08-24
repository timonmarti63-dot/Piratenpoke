using System.Collections;
using System.Collections.Generic;
using Unity.Cinemachine;
using UnityEngine;
using Piratenpoke.Data;
using Piratenpoke.SceneManagement;
using Piratenpoke.UI;

namespace Piratenpoke.Battle
{
    /// <summary>
    /// Rundenbasierter Kampf mit Cinemachine-Kamera-Wechseln.
    ///
    /// Nutzt <see cref="BattleContext.PendingEnemy"/>. Fuer die Party-Seite
    /// wird das Party-Roster aus <see cref="Inventory"/> gelesen (siehe unten).
    /// </summary>
    public class BattleManager : MonoBehaviour
    {
        [Header("Party (Fallback wenn Inventory leer)")]
        public CrewMemberSO[] fallbackParty;
        [SerializeField, Min(1)] private int fallbackLevel = 3;

        [Header("Spawn-Punkte")]
        public Transform playerSpawn;
        public Transform enemySpawn;

        [Header("Kameras (Cinemachine) -- optional; sonst Runtime-Rig")]
        public CinemachineCamera camWide;
        public CinemachineCamera camPlayer;
        public CinemachineCamera camEnemy;
        [SerializeField] private BattleCameraRig cameraRig;

        [Header("UI")]
        public BattleHUD hud;

        [Header("Timings")]
        [SerializeField, Range(0.2f, 3f)] private float introSeconds = 1.4f;
        [SerializeField, Range(0.1f, 2f)] private float actorFocusSeconds = 0.6f;
        [SerializeField, Range(0.1f, 2f)] private float impactHoldSeconds = 0.45f;
        [SerializeField, Range(0.05f, 1f)] private float postImpactPauseSeconds = 0.35f;

        private Combatant _player;
        private Combatant _enemy;
        private GameObject _playerModel;
        private GameObject _enemyModel;

        private void Start() => StartCoroutine(RunBattle());

        private IEnumerator RunBattle()
        {
            // -- 1. Feinddaten holen
            EnemyDataSO enemyData = BattleContext.PendingEnemy;
            if (enemyData == null)
            {
                Debug.LogWarning("BattleManager: kein PendingEnemy, Kampf abgebrochen.");
                EndBattle(BattleOutcome.PlayerFled);
                yield break;
            }

            // -- 2. Party-Fuehrer holen (Inventory.Active oder fallback[0])
            CrewMemberSO leader = Inventory.Active ?? (fallbackParty.Length > 0 ? fallbackParty[0] : null);
            if (leader == null)
            {
                Debug.LogError("BattleManager: kein Party-Leader.");
                EndBattle(BattleOutcome.PlayerFled); yield break;
            }
            _player = new Combatant(leader, leader.level, playerControlled: true);
            _enemy = new Combatant(enemyData, level: Mathf.Max(1, leader.level), playerControlled: false);

            // -- 3. Placeholder-Modelle spawnen
            _playerModel = MakeCapsule(_player, playerSpawn.position);
            _enemyModel = MakeCapsule(_enemy, enemySpawn.position);
            _playerModel.transform.LookAt(enemySpawn.position);
            _enemyModel.transform.LookAt(playerSpawn.position);

            // -- 4. Kamera-Rig bauen (falls nicht manuell verkabelt) und Ziele setzen
            EnsureCameraRig();
            cameraRig?.SetTargets(_playerModel.transform, _enemyModel.transform);

            // -- 5. HUD sicherstellen und initialisieren
            EnsureHud();
            hud.Initialize(_player, _enemy);

            // -- 6. Intro-Kamera (Wide)
            ActivateCam(camWide);
            yield return new WaitForSeconds(introSeconds);

            // -- 6. Runden bis KO oder Flucht
            while (_player.IsAlive && _enemy.IsAlive)
            {
                var order = OrderBySpeed();
                foreach (var actor in order)
                {
                    if (!_player.IsAlive || !_enemy.IsAlive) break;
                    if (!actor.IsAlive) continue;

                    yield return actor.IsPlayerControlled
                        ? PlayerTurn()
                        : EnemyTurn();

                    if (hud != null) hud.Refresh();
                    yield return new WaitForSeconds(0.35f);
                }
            }

            // -- 7. Ausgang
            BattleOutcome outcome = _player.IsAlive ? BattleOutcome.PlayerWin : BattleOutcome.EnemyWin;
            EndBattle(outcome);
        }

        private List<Combatant> OrderBySpeed()
        {
            var list = new List<Combatant> { _player, _enemy };
            list.Sort((a, b) => b.Speed.CompareTo(a.Speed));
            return list;
        }

        private IEnumerator PlayerTurn()
        {
            ActivateCam(camPlayer);
            yield return new WaitForSeconds(actorFocusSeconds);
            if (hud != null) hud.OpenActionMenu();

            // Warte auf Spielereingabe (HUD setzt PendingSkill)
            while (hud != null && hud.PendingSkill == null && !hud.PendingFlee)
                yield return null;

            if (hud != null && hud.PendingFlee)
            {
                hud.CloseActionMenu();
                BattleContext.LastOutcome = BattleOutcome.PlayerFled;
                EndBattle(BattleOutcome.PlayerFled);
                yield break;
            }

            SkillSO chosen = hud.PendingSkill;
            hud?.CloseActionMenu();

            yield return ResolveSkill(_player, _enemy, chosen, _playerModel, _enemyModel);
        }

        private IEnumerator EnemyTurn()
        {
            ActivateCam(camEnemy);
            yield return new WaitForSeconds(actorFocusSeconds);
            // Simple KI: zufaelliger Skill mit Praeferenz auf Offensive
            var skill = ChooseEnemySkill();
            yield return ResolveSkill(_enemy, _player, skill, _enemyModel, _playerModel);
            // Nach dem Enemy-Turn zurueck zur Uebersicht.
            ActivateCam(camWide);
        }

        private SkillSO ChooseEnemySkill()
        {
            if (_enemy.Data.skills == null || _enemy.Data.skills.Length == 0) return null;
            var list = _enemy.Data.skills;
            return list[Random.Range(0, list.Length)];
        }

        private IEnumerator ResolveSkill(Combatant caster, Combatant target, SkillSO skill,
                                        GameObject casterGo, GameObject targetGo)
        {
            if (skill == null) { yield return HighlightAndDamage(caster, target, 4, casterGo, targetGo); yield break; }

            if (skill.heal > 0)
            {
                caster.Heal(skill.heal);
                yield return Bump(casterGo, targetGo, up: true);
                yield break;
            }

            if (Random.value > skill.accuracy)
            {
                Debug.Log($"{caster.DisplayName} verfehlt {target.DisplayName}!");
                yield return Bump(casterGo, targetGo, up: false);
                yield break;
            }

            int damage = ComputeDamage(caster, target, skill);
            target.TakeDamage(damage);
            yield return HighlightAndDamage(caster, target, damage, casterGo, targetGo);
        }

        private int ComputeDamage(Combatant caster, Combatant target, SkillSO skill)
        {
            float mult = ElementMultiplier(skill.element, target.Element);
            return Mathf.RoundToInt((skill.power + caster.Attack * 0.6f) * mult);
        }

        private float ElementMultiplier(Element atk, Element def)
        {
            // Kleine Rock-Paper-Scissors-Tabelle: Fire>Wind>Stone>Water>Fire
            if (atk == Element.Fire && def == Element.Wind) return 1.5f;
            if (atk == Element.Wind && def == Element.Stone) return 1.5f;
            if (atk == Element.Stone && def == Element.Water) return 1.5f;
            if (atk == Element.Water && def == Element.Fire) return 1.5f;
            if (atk == def && atk != Element.None) return 0.75f;
            return 1f;
        }

        private IEnumerator HighlightAndDamage(Combatant caster, Combatant target,
                                              int damage, GameObject casterGo, GameObject targetGo)
        {
            // 1. Angreifer bewegt sich in Richtung Ziel (Bump).
            var bump = StartCoroutine(Bump(casterGo, targetGo, up: true));

            // 2. Kurz vor dem Impact snappt die Impact-Kamera aufs Ziel.
            yield return new WaitForSeconds(0.12f);
            if (cameraRig != null && casterGo != null && targetGo != null)
            {
                cameraRig.FocusImpact(targetGo.transform, casterGo.transform);
                cameraRig.Activate(cameraRig.CamImpact, fastCut: true);
            }

            // 3. Ziel wird rot markiert + kurzer Hold.
            if (targetGo != null)
            {
                var mr = targetGo.GetComponent<MeshRenderer>();
                var origColor = mr != null ? mr.material.color : Color.white;
                if (mr != null) mr.material.color = Color.red;
                yield return new WaitForSeconds(impactHoldSeconds);
                if (mr != null) mr.material.color = origColor;
            }
            else
            {
                yield return new WaitForSeconds(impactHoldSeconds);
            }

            // 4. Bump auslaufen lassen und dann kurze Verschnaufpause.
            if (bump != null) yield return bump;
            yield return new WaitForSeconds(postImpactPauseSeconds);
        }

        private IEnumerator Bump(GameObject a, GameObject b, bool up)
        {
            if (a == null || b == null) yield break;
            Vector3 start = a.transform.position;
            Vector3 dir = (b.transform.position - a.transform.position).normalized;
            Vector3 peak = start + dir * 0.6f + (up ? Vector3.up * 0.3f : Vector3.zero);
            float t = 0f, dur = 0.15f;
            while (t < dur) { a.transform.position = Vector3.Lerp(start, peak, t / dur); t += Time.deltaTime; yield return null; }
            t = 0f;
            while (t < dur) { a.transform.position = Vector3.Lerp(peak, start, t / dur); t += Time.deltaTime; yield return null; }
            a.transform.position = start;
        }

        private void EnsureHud()
        {
            if (hud != null) return;
            var hudGo = new GameObject("BattleHUD");
            hudGo.transform.SetParent(transform, false);
            hud = hudGo.AddComponent<BattleHUD>();
        }

        private void EnsureCameraRig()
        {
            if (cameraRig == null)
            {
                var rigGo = new GameObject("BattleCameraRig");
                rigGo.transform.SetParent(transform, false);
                cameraRig = rigGo.AddComponent<BattleCameraRig>();
            }
            cameraRig.BuildIfNeeded();

            // Serialized-Field-Kameras nur setzen, wenn im Editor nichts verdrahtet ist.
            if (camWide == null) camWide = cameraRig.CamWide;
            if (camPlayer == null) camPlayer = cameraRig.CamPlayer;
            if (camEnemy == null) camEnemy = cameraRig.CamEnemy;
        }

        private void ActivateCam(CinemachineCamera cam)
        {
            if (cam == null) return;
            if (cameraRig != null)
            {
                cameraRig.Activate(cam);
                return;
            }
            // Fallback ohne Rig: nur Priority setzen.
            if (camWide != null) camWide.Priority = 10;
            if (camPlayer != null) camPlayer.Priority = 10;
            if (camEnemy != null) camEnemy.Priority = 10;
            cam.Priority = 20;
        }

        private GameObject MakeCapsule(Combatant c, Vector3 pos)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            go.name = c.DisplayName;
            go.transform.position = pos;
            var mr = go.GetComponent<MeshRenderer>();
            if (mr != null) mr.material.color = c.Data.placeholderColor;
            return go;
        }

        private void EndBattle(BattleOutcome outcome)
        {
            BattleContext.LastOutcome = outcome;

            // Encounter benachrichtigen (falls Overworld-Feind uebrig)
            var patrol = BattleContext.PendingSourcePatrol;
            if (patrol != null)
            {
                if (outcome == BattleOutcome.PlayerWin) patrol.OnBattleWon();
                else if (outcome == BattleOutcome.PlayerFled) patrol.OnPlayerFled();
            }

            SceneRouter.Instance?.LeaveBattle();
        }
    }
}
