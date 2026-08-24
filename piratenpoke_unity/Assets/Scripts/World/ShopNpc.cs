using UnityEngine;
using Piratenpoke.Data;
using Piratenpoke.Player;
using Piratenpoke.UI;

namespace Piratenpoke.World
{
    /// <summary>
    /// NPC-Haendler: bei Interaction oeffnet sich das Shop-UI.
    /// </summary>
    public class ShopNpc : MonoBehaviour, IInteractable
    {
        public string shopTitle = "Apotheke";
        public ItemSO[] stock;
        public ShopUI shopUI;

        public string PromptText => $"E: {shopTitle} betreten";

        public void Interact(PlayerController3D _)
        {
            if (shopUI == null) shopUI = FindFirstObjectByType<ShopUI>(FindObjectsInactive.Include);
            if (shopUI == null)
            {
                Debug.LogWarning("ShopNpc: kein ShopUI in der Scene.", this);
                return;
            }
            shopUI.Open(shopTitle, stock);
        }
    }
}
