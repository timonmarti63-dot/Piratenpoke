using UnityEngine;
using UnityEngine.SceneManagement;
using Piratenpoke.Data;
using Piratenpoke.SceneManagement;

namespace Piratenpoke.Utils
{
    /// <summary>
    /// Legt Startpunkt fest: laedt Default-Party in Inventory, sofern leer.
    /// Kann per Menu > "Piratenpoke > Reset Boot" reinitialisiert werden.
    /// </summary>
    public class BootStrap : MonoBehaviour
    {
        [Header("Default Party (bei leerem Inventar)")]
        public CrewMemberSO[] defaultParty;

        [Header("Default Items")]
        public ItemSO[] defaultItems;
        [Min(0)] public int defaultGold = 100;

        private void Awake()
        {
            if (Inventory.Crew.Count == 0 && defaultParty != null)
            {
                foreach (var c in defaultParty) Inventory.AddCrew(c);
            }
            if (Inventory.Items.Count == 0 && defaultItems != null)
            {
                foreach (var i in defaultItems) Inventory.AddItem(i, 1);
            }
            if (Inventory.Gold <= 0) Inventory.Gold = defaultGold;
        }

        private void Start()
        {
            // Boot-Scene ist nur der Autoload-Punkt -- danach in die Testinsel wechseln.
            if (SceneManager.GetActiveScene().name == "Boot")
                SceneManager.LoadScene(SceneRouter.OverworldTestScene);
        }
    }
}
