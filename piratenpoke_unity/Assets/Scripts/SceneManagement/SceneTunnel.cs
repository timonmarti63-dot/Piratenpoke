using UnityEngine;

namespace Piratenpoke.SceneManagement
{
    /// <summary>
    /// Trigger-Zone: laeuft der Player hinein, wird per SceneRouter in die
    /// Zielszene gewechselt. Modelliert "Tunnel" zwischen Zonen wie in Sw/Sh.
    /// </summary>
    [RequireComponent(typeof(Collider))]
    public class SceneTunnel : MonoBehaviour
    {
        public enum TargetScene { Overworld, Village, Battle }
        [SerializeField] private TargetScene target = TargetScene.Village;

        private void Reset()
        {
            var c = GetComponent<Collider>();
            if (c != null) c.isTrigger = true;
        }

        private void OnTriggerEnter(Collider other)
        {
            if (!other.CompareTag("Player")) return;
            if (SceneRouter.Instance == null)
            {
                Debug.LogWarning("SceneTunnel: kein SceneRouter in der Scene.", this);
                return;
            }
            switch (target)
            {
                case TargetScene.Overworld: SceneRouter.Instance.EnterOverworld(); break;
                case TargetScene.Village:   SceneRouter.Instance.EnterVillage(); break;
                case TargetScene.Battle:    SceneRouter.Instance.EnterBattle(); break;
            }
        }
    }
}
