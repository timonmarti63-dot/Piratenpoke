using Piratenpoke.Data;
using Piratenpoke.Encounter;

namespace Piratenpoke.SceneManagement
{
    /// <summary>
    /// Statischer Bridge-Zustand zwischen Overworld und Battle-Scene.
    /// Wird vor EnterBattle() vom Encounter gesetzt und in der Battle-Scene
    /// vom BattleManager gelesen.
    /// </summary>
    public static class BattleContext
    {
        public static EnemyDataSO PendingEnemy;
        public static EnemyPatrol PendingSourcePatrol;
        public static BattleOutcome LastOutcome = BattleOutcome.None;
    }

    public enum BattleOutcome { None, PlayerWin, PlayerFled, EnemyWin }
}
