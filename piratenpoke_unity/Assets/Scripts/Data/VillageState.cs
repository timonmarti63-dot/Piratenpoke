using System;
using System.Collections.Generic;

namespace Piratenpoke.Data
{
    /// <summary>
    /// Globaler Village-Zustand (isSafe pro Dorf). Autoload-Aequivalent des
    /// alten Godot-Skripts.
    /// </summary>
    public static class VillageState
    {
        public static event Action<string> VillageLiberated;

        private static readonly HashSet<string> _defeatedLeaders = new();
        private static readonly HashSet<string> _safeVillages = new();

        public static void MarkLeaderDefeated(string leaderId)
        {
            if (string.IsNullOrEmpty(leaderId) || !_defeatedLeaders.Add(leaderId)) return;

            // Konvention: leaderId = "<village>_captain" => safe = <village>
            string village = leaderId.Replace("_captain", "");
            if (_safeVillages.Add(village))
                VillageLiberated?.Invoke(village);
        }

        public static bool IsSafe(string village) => _safeVillages.Contains(village);
    }
}
