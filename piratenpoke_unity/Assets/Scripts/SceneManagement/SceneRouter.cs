using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Piratenpoke.SceneManagement
{
    /// <summary>
    /// Zentrale Scene-Verwaltung mit Fade-Uebergaengen (Switch-Feeling).
    ///
    /// Overworld -> Battle: Save Overworld-Snapshot, laden Battle-Scene additiv,
    /// Overworld deaktiviert (nicht ausgeladen) fuer schnelle Rueckkehr.
    ///
    /// Erwartet ein DontDestroyOnLoad-Objekt in der Boot-Scene. Wenn keins da ist,
    /// wird es beim ersten Zugriff angelegt.
    /// </summary>
    public class SceneRouter : MonoBehaviour
    {
        public static SceneRouter Instance { get; private set; }

        public const string OverworldTestScene = "TestIsland";
        public const string VillageScene = "VillageKelpholm";
        public const string BattleScene = "BattleArena";

        [SerializeField] private FadeOverlay fadeOverlay;

        [Header("Fade-Timings (Sekunden)")]
        [SerializeField, Min(0f)] private float fadeOutTime = 0.4f;
        [SerializeField, Min(0f)] private float fadeInTime = 0.5f;

        private string _pendingReturnScene;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);

            if (fadeOverlay == null)
                fadeOverlay = GetComponentInChildren<FadeOverlay>(includeInactive: true);
        }

        public void EnterBattle() => StartCoroutine(SwitchTo(BattleScene, remember: true));
        public void LeaveBattle() => StartCoroutine(ReturnToRemembered());
        public void EnterVillage() => StartCoroutine(SwitchTo(VillageScene, remember: false));
        public void EnterOverworld() => StartCoroutine(SwitchTo(OverworldTestScene, remember: false));

        private IEnumerator SwitchTo(string target, bool remember)
        {
            if (fadeOverlay != null) yield return fadeOverlay.FadeOut(fadeOutTime);

            if (remember) _pendingReturnScene = SceneManager.GetActiveScene().name;

            var op = SceneManager.LoadSceneAsync(target, LoadSceneMode.Single);
            while (!op.isDone) yield return null;

            if (fadeOverlay != null) yield return fadeOverlay.FadeIn(fadeInTime);
        }

        private IEnumerator ReturnToRemembered()
        {
            if (string.IsNullOrEmpty(_pendingReturnScene))
                _pendingReturnScene = OverworldTestScene;

            if (fadeOverlay != null) yield return fadeOverlay.FadeOut(fadeOutTime);
            var op = SceneManager.LoadSceneAsync(_pendingReturnScene, LoadSceneMode.Single);
            while (!op.isDone) yield return null;
            if (fadeOverlay != null) yield return fadeOverlay.FadeIn(fadeInTime);
        }
    }
}
