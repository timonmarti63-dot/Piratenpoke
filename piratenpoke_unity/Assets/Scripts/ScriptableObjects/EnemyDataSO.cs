using UnityEngine;

namespace Piratenpoke.Data
{
    /// <summary>AI-Profile fuer Gegner-Verhalten in der Runde.</summary>
    public enum AIProfile { Aggressive, Defensive, Balanced, Trickster }

    /// <summary>Gegner-Definition + Belohnungen bei Sieg.</summary>
    [CreateAssetMenu(fileName = "Enemy_New", menuName = "Piratenpoke/Enemy")]
    public class EnemyDataSO : CombatantSO
    {
        [Header("Belohnung")]
        public int xpReward = 15;
        public int goldReward = 10;

        [Header("Verhalten")]
        public AIProfile aiProfile = AIProfile.Balanced;
        [Tooltip("Boss = Belohnungen x2 + spezielle Kamera im Kampf.")]
        public bool isBoss = false;

        [Header("Optional: Truppenfuehrer")]
        [Tooltip("Wenn gesetzt: Sieg befreit das zugehoerige Dorf (isSafe = true).")]
        public string troopLeaderId = "";
    }
}
