using UnityEngine;
using Piratenpoke.Data;

namespace Piratenpoke.Battle
{
    /// <summary>
    /// Laufzeit-Zustand eines Kampfteilnehmers (aktuelle HP, Gift, Cooldowns).
    /// Referenziert ein <see cref="CombatantSO"/> fuer Basis-Stats -- so bleibt
    /// die SO-Definition unveraendert.
    /// </summary>
    public class Combatant
    {
        public CombatantSO Data { get; }
        public int CurrentHp;
        public bool IsPoisoned;
        public bool IsPlayerControlled;
        public int Level;

        public int MaxHp => Data.maxHp + (Level - 1) * 4;
        public int Attack => Data.baseAttack + (Level - 1) * 2;
        public int Defense => Data.baseDefense + (Level - 1);
        public int Speed => Data.speed;
        public Element Element => Data.element;
        public string DisplayName => Data.displayName;

        public bool IsAlive => CurrentHp > 0;

        public Combatant(CombatantSO data, int level, bool playerControlled)
        {
            Data = data;
            Level = Mathf.Max(1, level);
            IsPlayerControlled = playerControlled;
            CurrentHp = MaxHp;
        }

        public int TakeDamage(int amount)
        {
            int actual = Mathf.Max(1, amount - Defense / 3);
            CurrentHp = Mathf.Max(0, CurrentHp - actual);
            return actual;
        }

        public int Heal(int amount)
        {
            int before = CurrentHp;
            CurrentHp = Mathf.Min(MaxHp, CurrentHp + amount);
            return CurrentHp - before;
        }
    }
}
