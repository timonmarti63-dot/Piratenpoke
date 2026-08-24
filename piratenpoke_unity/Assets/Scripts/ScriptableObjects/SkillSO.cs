using UnityEngine;

namespace Piratenpoke.Data
{
    /// <summary>Element eines Skills oder Charakters.</summary>
    public enum Element { None, Fire, Water, Stone, Wind }

    /// <summary>Zielauswahl fuer einen Skill.</summary>
    public enum SkillTarget { SingleEnemy, AllEnemies, SelfAlly, AllAllies }

    /// <summary>
    /// Visuelle Kategorie fuer die Runtime-Effekt-Bibliothek. Steuert welcher
    /// Particle-/Beam-/Trail-Effekt beim Einsatz gespielt wird.
    /// </summary>
    public enum SkillVfx
    {
        None,
        Slash,       // Nahkampf-Schnittbogen (Feuerhieb, Rostklinge)
        Projectile,  // Kleines gerichtetes Geschoss (Flutschuss, Giftdart)
        Burst,       // Explosion um das Ziel (Sturmboe, Feuerknall)
        Heal,        // Aufsteigende Heilpartikel um den Selbst-Wirker
        Beam         // Kontinuierlicher Strahl vom Wirker zum Ziel
    }

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

        [Header("Visueller Effekt")]
        public SkillVfx vfx = SkillVfx.None;
        [Tooltip("Hauptfarbe des Effekts. Wenn transparent, wird die Element-Farbe verwendet.")]
        public Color vfxColor = new Color(1f, 1f, 1f, 0f);
        [Tooltip("Effekt-Dauer in Sekunden (0 = Standardwert der Kategorie).")]
        [Range(0f, 3f)] public float vfxDuration = 0f;
    }
}
