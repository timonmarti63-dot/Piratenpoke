using UnityEngine;
using Piratenpoke.Data;

namespace Piratenpoke.World
{
    /// <summary>
    /// Root-Skript einer Dorf-Szene.
    ///
    /// * enemyGroup: Container mit patrouillierenden Gegnern
    /// * safeGroup:  Container mit friedlichen NPCs & Haendlern
    ///
    /// Aktiviert / deaktiviert je nach VillageState.IsSafe(villageId).
    /// </summary>
    public class VillageController : MonoBehaviour
    {
        public string villageId = "kelpholm";
        public GameObject enemyGroup;
        public GameObject safeGroup;

        private void OnEnable()  => VillageState.VillageLiberated += OnLiberated;
        private void OnDisable() => VillageState.VillageLiberated -= OnLiberated;

        private void Start() => ApplyState();

        private void OnLiberated(string v) { if (v == villageId) ApplyState(); }

        private void ApplyState()
        {
            bool safe = VillageState.IsSafe(villageId);
            if (enemyGroup != null) enemyGroup.SetActive(!safe);
            if (safeGroup != null)  safeGroup.SetActive(safe);
        }
    }
}
