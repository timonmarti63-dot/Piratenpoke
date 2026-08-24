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
            AutoBuildIfMissing();
            if (playerName != null) playerName.text = $"{player.DisplayName}  Lv.{player.Level}";
            if (enemyName != null) enemyName.text = $"{enemy.DisplayName}";
            if (fleeButton != null)
                fleeButton.onClick.AddListener(() => PendingFlee = true);
            CloseActionMenu();
            Refresh();
        }

        /// <summary>
        /// Baut zur Laufzeit ein Minimal-HUD auf, wenn nichts im Editor verkabelt ist.
        /// So laeuft der Kampf sofort, auch bevor der Nutzer eine .prefab-Kette anlegt.
        /// </summary>
        private void AutoBuildIfMissing()
        {
            if (playerHpBar != null && enemyHpBar != null && actionMenuRoot != null && skillButtonPrefab != null)
                return;

            // -- Canvas + Skalierung
            var canvasGo = new GameObject("BattleHUD_Canvas");
            canvasGo.transform.SetParent(transform, false);
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasGo.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            scaler.matchWidthOrHeight = 0.5f;
            canvasGo.AddComponent<GraphicRaycaster>();

            // EventSystem sicherstellen (sonst reagieren Buttons nicht).
            if (FindObjectOfType<UnityEngine.EventSystems.EventSystem>() == null)
            {
                var esGo = new GameObject("EventSystem");
                esGo.AddComponent<UnityEngine.EventSystems.EventSystem>();
                esGo.AddComponent<UnityEngine.EventSystems.StandaloneInputModule>();
            }

            // -- Enemy-Panel oben rechts
            enemyName = enemyName ?? CreateText(canvasGo.transform, "EnemyName",
                new Vector2(1, 1), new Vector2(1, 1), new Vector2(-380, -60), new Vector2(340, 40), 30, TextAlignmentOptions.Right);
            enemyHpBar = enemyHpBar ?? CreateSlider(canvasGo.transform, "EnemyHp",
                new Vector2(1, 1), new Vector2(1, 1), new Vector2(-380, -105), new Vector2(340, 22));
            enemyHpText = enemyHpText ?? CreateText(canvasGo.transform, "EnemyHpText",
                new Vector2(1, 1), new Vector2(1, 1), new Vector2(-380, -135), new Vector2(340, 24), 20, TextAlignmentOptions.Right);

            // -- Player-Panel unten links
            playerName = playerName ?? CreateText(canvasGo.transform, "PlayerName",
                new Vector2(0, 0), new Vector2(0, 0), new Vector2(220, 220), new Vector2(340, 40), 30, TextAlignmentOptions.Left);
            playerHpBar = playerHpBar ?? CreateSlider(canvasGo.transform, "PlayerHp",
                new Vector2(0, 0), new Vector2(0, 0), new Vector2(220, 180), new Vector2(340, 22));
            playerHpText = playerHpText ?? CreateText(canvasGo.transform, "PlayerHpText",
                new Vector2(0, 0), new Vector2(0, 0), new Vector2(220, 150), new Vector2(340, 24), 20, TextAlignmentOptions.Left);

            // -- Aktions-Menue unten rechts
            if (actionMenuRoot == null)
            {
                var menuGo = new GameObject("ActionMenu", typeof(RectTransform));
                menuGo.transform.SetParent(canvasGo.transform, false);
                var rt = (RectTransform)menuGo.transform;
                rt.anchorMin = new Vector2(1, 0);
                rt.anchorMax = new Vector2(1, 0);
                rt.pivot = new Vector2(1, 0);
                rt.anchoredPosition = new Vector2(-40, 40);
                rt.sizeDelta = new Vector2(360, 260);
                var bg = menuGo.AddComponent<Image>();
                bg.color = new Color(0f, 0f, 0f, 0.55f);
                var layout = menuGo.AddComponent<VerticalLayoutGroup>();
                layout.padding = new RectOffset(14, 14, 14, 14);
                layout.spacing = 6;
                layout.childControlHeight = false;
                layout.childControlWidth = true;
                layout.childForceExpandHeight = false;
                layout.childForceExpandWidth = true;
                actionMenuRoot = menuGo.transform;
            }

            if (skillButtonPrefab == null)
                skillButtonPrefab = BuildSkillButtonPrefab();

            if (fleeButton == null)
            {
                var flee = Instantiate(skillButtonPrefab, canvasGo.transform);
                flee.name = "FleeButton";
                var flt = flee.GetComponentInChildren<TextMeshProUGUI>();
                if (flt != null) flt.text = "Fliehen";
                var frt = (RectTransform)flee.transform;
                frt.anchorMin = new Vector2(1, 0);
                frt.anchorMax = new Vector2(1, 0);
                frt.pivot = new Vector2(1, 0);
                frt.anchoredPosition = new Vector2(-40, 320);
                frt.sizeDelta = new Vector2(200, 44);
                fleeButton = flee;
            }
        }

        private TextMeshProUGUI CreateText(Transform parent, string label,
            Vector2 anchorMin, Vector2 anchorMax, Vector2 pos, Vector2 size,
            float fontSize, TextAlignmentOptions align)
        {
            var go = new GameObject(label, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var rt = (RectTransform)go.transform;
            rt.anchorMin = anchorMin; rt.anchorMax = anchorMax; rt.pivot = new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = pos; rt.sizeDelta = size;
            var tmp = go.AddComponent<TextMeshProUGUI>();
            tmp.fontSize = fontSize;
            tmp.alignment = align;
            tmp.color = Color.white;
            tmp.text = label;
            return tmp;
        }

        private Slider CreateSlider(Transform parent, string label,
            Vector2 anchorMin, Vector2 anchorMax, Vector2 pos, Vector2 size)
        {
            var go = new GameObject(label, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var rt = (RectTransform)go.transform;
            rt.anchorMin = anchorMin; rt.anchorMax = anchorMax; rt.pivot = new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = pos; rt.sizeDelta = size;

            var bg = new GameObject("BG", typeof(RectTransform));
            bg.transform.SetParent(go.transform, false);
            var bgRt = (RectTransform)bg.transform;
            bgRt.anchorMin = Vector2.zero; bgRt.anchorMax = Vector2.one;
            bgRt.sizeDelta = Vector2.zero;
            var bgImg = bg.AddComponent<Image>();
            bgImg.color = new Color(0f, 0f, 0f, 0.6f);

            var fillArea = new GameObject("Fill Area", typeof(RectTransform));
            fillArea.transform.SetParent(go.transform, false);
            var faRt = (RectTransform)fillArea.transform;
            faRt.anchorMin = new Vector2(0, 0.15f); faRt.anchorMax = new Vector2(1, 0.85f);
            faRt.offsetMin = new Vector2(4, 0); faRt.offsetMax = new Vector2(-4, 0);

            var fill = new GameObject("Fill", typeof(RectTransform));
            fill.transform.SetParent(fillArea.transform, false);
            var fillRt = (RectTransform)fill.transform;
            fillRt.anchorMin = Vector2.zero; fillRt.anchorMax = Vector2.one;
            fillRt.sizeDelta = Vector2.zero;
            var fillImg = fill.AddComponent<Image>();
            fillImg.color = new Color(0.32f, 0.87f, 0.35f, 1f);

            var slider = go.AddComponent<Slider>();
            slider.transition = Selectable.Transition.None;
            slider.fillRect = fillRt;
            slider.direction = Slider.Direction.LeftToRight;
            slider.minValue = 0; slider.maxValue = 1; slider.value = 1;
            return slider;
        }

        private Button BuildSkillButtonPrefab()
        {
            var go = new GameObject("SkillButtonPrefab", typeof(RectTransform));
            go.transform.SetParent(transform, false);
            var rt = (RectTransform)go.transform;
            rt.sizeDelta = new Vector2(320, 44);
            var img = go.AddComponent<Image>();
            img.color = new Color(0.13f, 0.16f, 0.24f, 0.95f);
            var btn = go.AddComponent<Button>();
            var colors = btn.colors;
            colors.highlightedColor = new Color(0.28f, 0.4f, 0.7f, 1f);
            btn.colors = colors;

            var textGo = new GameObject("Label", typeof(RectTransform));
            textGo.transform.SetParent(go.transform, false);
            var trt = (RectTransform)textGo.transform;
            trt.anchorMin = Vector2.zero; trt.anchorMax = Vector2.one; trt.sizeDelta = Vector2.zero;
            var tmp = textGo.AddComponent<TextMeshProUGUI>();
            tmp.text = "Skill";
            tmp.color = Color.white;
            tmp.fontSize = 22;
            tmp.alignment = TextAlignmentOptions.Center;

            // Prefab-Objekt inaktiv, Instantiate reaktiviert es.
            go.SetActive(false);
            return btn;
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
