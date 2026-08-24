using UnityEngine;

namespace Piratenpoke.Data
{
    /// <summary>
    /// Basisklasse fuer Crew und Gegner. Enthaelt nur statische Stats.
    /// Kampf-Laufzeit (aktuelle HP, Buffs) lebt in <see cref="Combat.Combatant"/>,
    /// nicht hier -- so bleiben ScriptableObjects deterministisch und
    /// wiederverwendbar zwischen Kaempfen.
    /// </summary>
    public abstract class CombatantSO : ScriptableObject
    {
        [Header("Anzeige")]
        public string displayName = "Unbekannt";
        public Element element = Element.None;
        [Tooltip("Optional: Farbe der Platzhalter-Kapsel bis 3D-Modelle vorliegen.")]
        public Color placeholderColor = Color.white;

        [Header("Basis-Attribute")]
        public int maxHp = 40;
        public int baseAttack = 10;
        public int baseDefense = 6;
        [Tooltip("Bestimmt die Zugreihenfolge in der Runden-Initiative.")]
        public int speed = 8;

        [Header("Skills (max 4)")]
        public SkillSO[] skills = new SkillSO[0];
    }
}
