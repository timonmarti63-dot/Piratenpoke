using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Piratenpoke.Data;

namespace Piratenpoke.UI
{
    /// <summary>Einfacher Shop-Screen. Kauft aus einem festen Angebot.</summary>
    public class ShopUI : MonoBehaviour
    {
        public GameObject root;
        public TextMeshProUGUI titleLabel;
        public TextMeshProUGUI goldLabel;
        public Transform listRoot;
        public Button rowPrefab;
        public Button closeButton;

        private readonly List<GameObject> _rows = new();

        private void Awake()
        {
            if (root == null) root = gameObject;
            root.SetActive(false);
            if (closeButton != null) closeButton.onClick.AddListener(Close);
        }

        public void Open(string title, ItemSO[] stock)
        {
            root.SetActive(true);
            if (titleLabel != null) titleLabel.text = title;
            Rebuild(stock);
            RefreshGold();
        }

        public void Close() => root.SetActive(false);

        private void Rebuild(ItemSO[] stock)
        {
            foreach (var r in _rows) Destroy(r);
            _rows.Clear();
            if (listRoot == null || rowPrefab == null) return;
            foreach (var item in stock)
            {
                if (item == null) continue;
                var btn = Instantiate(rowPrefab, listRoot);
                var label = btn.GetComponentInChildren<TextMeshProUGUI>();
                if (label != null) label.text = $"{item.displayName} — {item.buyPrice} G";
                btn.onClick.AddListener(() =>
                {
                    if (Inventory.Buy(item)) RefreshGold();
                });
                _rows.Add(btn.gameObject);
            }
        }

        private void RefreshGold()
        {
            if (goldLabel != null) goldLabel.text = $"Gold: {Inventory.Gold}";
        }
    }
}
