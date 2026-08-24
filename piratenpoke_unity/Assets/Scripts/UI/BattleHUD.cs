using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Piratenpoke.Battle;
using Piratenpoke.Data;

namespace Piratenpoke.UI
{
    /// <summary>
    /// Kampf-Overlay: HP-Balken, Namen, Skill-Buttons. Nutzt vorhandene
    /// TMP-Referenzen. Wenn keine vorhanden sind, wird ein Minimal-Canvas
    /// zur Laufzeit angelegt.
    /// </summary>
    public class BattleHUD : MonoBehaviour
    {
        [Header("Player-Seite")]
        public TextMeshProUGUI playerName;
        public Slider playerHpBar;
        public TextMeshProUGUI playerHpText;

        [Header("Enemy-Seite")]
        public TextMeshProUGUI enemyName;
        public Slider enemyHpBar;
        public TextMeshProUGUI enemyHpText;

        [Header("Aktionen")]
        public Transform actionMenuRoot;
        public Button skillButtonPrefab;
        public Button fleeButton;

        public SkillSO PendingSkill { get; private set; }
        public bool PendingFlee { get; private set; }

        private Combatant _player;
        private Combatant _enemy;
        private readonly List<GameObject> _spawnedButtons = new();

        public void Initialize(Combatant player, Combatant enemy)
        {
            _player = player; _enemy = enemy;
            if (playerName != null) playerName.text = $"{player.DisplayName}  Lv.{player.Level}";
            if (enemyName != null) enemyName.text = $"{enemy.DisplayName}";
            if (fleeButton != null)
                fleeButton.onClick.AddListener(() => PendingFlee = true);
            CloseActionMenu();
            Refresh();
        }

        public void Refresh()
        {
            if (_player != null)
            {
                if (playerHpBar != null) { playerHpBar.maxValue = _player.MaxHp; playerHpBar.value = _player.CurrentHp; }
                if (playerHpText != null) playerHpText.text = $"{_player.CurrentHp} / {_player.MaxHp}";
            }
            if (_enemy != null)
            {
                if (enemyHpBar != null) { enemyHpBar.maxValue = _enemy.MaxHp; enemyHpBar.value = _enemy.CurrentHp; }
                if (enemyHpText != null) enemyHpText.text = $"{_enemy.CurrentHp} / {_enemy.MaxHp}";
            }
        }

        public void OpenActionMenu()
        {
            PendingSkill = null; PendingFlee = false;
            if (actionMenuRoot == null || skillButtonPrefab == null) return;
            ClearButtons();
            actionMenuRoot.gameObject.SetActive(true);
            foreach (var skill in _player.Data.skills)
            {
                if (skill == null) continue;
                var btn = Instantiate(skillButtonPrefab, actionMenuRoot);
                var label = btn.GetComponentInChildren<TextMeshProUGUI>();
                if (label != null) label.text = $"{skill.displayName}  ({skill.element})";
                btn.onClick.AddListener(() => PendingSkill = skill);
                _spawnedButtons.Add(btn.gameObject);
            }
        }

        public void CloseActionMenu()
        {
            if (actionMenuRoot != null) actionMenuRoot.gameObject.SetActive(false);
            ClearButtons();
        }

        private void ClearButtons()
        {
            foreach (var go in _spawnedButtons) Destroy(go);
            _spawnedButtons.Clear();
        }
    }
}
