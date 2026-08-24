using UnityEngine;

namespace Piratenpoke.Data
{
    /// <summary>Ein Crew-Mitglied des Spielers. Enthaelt Fortschritt (Level/XP).</summary>
    [CreateAssetMenu(fileName = "Crew_New", menuName = "Piratenpoke/Crew Member")]
    public class CrewMemberSO : CombatantSO
    {
        [Header("Fortschritt")]
        [Min(1)] public int level = 1;
        public int xp = 0;

        [Header("Equipment (Referenzen ins Inventar)")]
        public ItemSO weapon;
        public ItemSO armor;
    }
}
