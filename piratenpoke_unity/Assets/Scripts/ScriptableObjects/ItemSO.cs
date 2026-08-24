using UnityEngine;

namespace Piratenpoke.Data
{
    public enum ItemCategory { Consumable, Weapon, Armor, KeyItem }

    /// <summary>
    /// Ein einzelner Inventar-Eintrag. Waffen/Ruestungen haben Modifiers,
    /// Consumables haben heal/cure Werte.
    /// </summary>
    [CreateAssetMenu(fileName = "Item_New", menuName = "Piratenpoke/Item")]
    public class ItemSO : ScriptableObject
    {
        [Header("Anzeige")]
        public string displayName = "Neues Item";
        [TextArea(2, 4)] public string description;

        [Header("Kategorie & Preis")]
        public ItemCategory category = ItemCategory.Consumable;
        public int buyPrice = 10;
        public int sellPrice = 5;

        [Header("Consumable")]
        [Tooltip("HP-Heilung wenn eingesetzt (0 = keine).")]
        public int healAmount = 0;
        [Tooltip("Heilt Gift.")]
        public bool curesPoison = false;

        [Header("Equipment Modifier")]
        public int attackBonus = 0;
        public int defenseBonus = 0;
        public int speedBonus = 0;
        public Element elementBonus = Element.None;
    }
}
