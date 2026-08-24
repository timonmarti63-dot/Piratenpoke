using UnityEngine;

namespace Piratenpoke.Data
{
    /// <summary>Element eines Skills oder Charakters.</summary>
    public enum Element { None, Fire, Water, Stone, Wind }

    /// <summary>Zielauswahl fuer einen Skill.</summary>
    public enum SkillTarget { SingleEnemy, AllEnemies, SelfAlly, AllAllies }

    /// <summary>
    /// Ein einsetzbarer Kampf-Skill. Rein datentragend, keine Kampf-Laufzeit.
    /// Portiert von data/skills/*.tres aus dem Godot-2D-Vorprojekt.
    /// </summary>
    [CreateAssetMenu(fileName = "Skill_New", menuName = "Piratenpoke/Skill")]
    public class SkillSO : ScriptableObject
    {
        [Header("Anzeige")]
        public string displayName = "Neuer Skill";
        [TextArea(2, 4)] public string description;

        [Header("Kampf")]
        public Element element = Element.None;
        public SkillTarget target = SkillTarget.SingleEnemy;
        [Tooltip("Basis-Schaden. 0 = kein Schaden (Heal/Buff).")]
        public int power = 10;
        [Tooltip("Heilung. 0 = kein Heal.")]
        public int heal = 0;
        [Range(0f, 1f)] public float accuracy = 0.95f;
        [Tooltip("Wie viele Runden Cooldown nach Einsatz.")]
        public int cooldown = 0;
    }
}
