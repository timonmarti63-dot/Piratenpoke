using System.Collections.Generic;
using UnityEngine;
using Piratenpoke.Data;

namespace Piratenpoke.Data
{
    /// <summary>
    /// Globales Inventar + Party. Statisch (Autoload-Ersatz). Wird in einer
    /// Boot-Scene oder BootStrap.cs initialisiert.
    /// </summary>
    public static class Inventory
    {
        public static readonly List<CrewMemberSO> Crew = new();
        public static readonly Dictionary<ItemSO, int> Items = new();
        public static int Gold = 100;
        public static int ActiveIndex = 0;

        public static CrewMemberSO Active =>
            (ActiveIndex >= 0 && ActiveIndex < Crew.Count) ? Crew[ActiveIndex] : null;

        public static void AddCrew(CrewMemberSO c) { if (c != null && !Crew.Contains(c)) Crew.Add(c); }
        public static void AddItem(ItemSO item, int count = 1)
        {
            if (item == null) return;
            Items.TryGetValue(item, out int have);
            Items[item] = have + count;
        }
        public static bool ConsumeItem(ItemSO item)
        {
            if (item == null) return false;
            if (!Items.TryGetValue(item, out int have) || have <= 0) return false;
            if (have <= 1) Items.Remove(item);
            else Items[item] = have - 1;
            return true;
        }
        public static bool Buy(ItemSO item)
        {
            if (item == null || Gold < item.buyPrice) return false;
            Gold -= item.buyPrice;
            AddItem(item, 1);
            return true;
        }
    }
}
