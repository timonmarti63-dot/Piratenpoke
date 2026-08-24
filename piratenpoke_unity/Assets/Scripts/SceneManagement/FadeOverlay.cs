using System.Collections;
using UnityEngine;
using UnityEngine.UI;

namespace Piratenpoke.SceneManagement
{
    /// <summary>
    /// Vollflaechiger schwarzer UI-Screen fuer Fade-in/out.
    /// Legt zur Laufzeit einen Canvas + Image an, falls keiner konfiguriert ist.
    /// </summary>
    public class FadeOverlay : MonoBehaviour
    {
        [SerializeField] private Image blackFill;

        private void Awake()
        {
            if (blackFill == null) Build();
            blackFill.color = new Color(0f, 0f, 0f, 0f);
        }

        private void Build()
        {
            var canvasGo = new GameObject("FadeCanvas");
            canvasGo.transform.SetParent(transform, false);

            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 9999;
            canvasGo.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            canvasGo.AddComponent<GraphicRaycaster>();

            var imgGo = new GameObject("Black");
            imgGo.transform.SetParent(canvasGo.transform, false);
            blackFill = imgGo.AddComponent<Image>();
            blackFill.color = new Color(0f, 0f, 0f, 0f);
            var rt = blackFill.rectTransform;
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
            blackFill.raycastTarget = false;
        }

        public IEnumerator FadeOut(float duration) => Fade(0f, 1f, duration);
        public IEnumerator FadeIn(float duration)  => Fade(1f, 0f, duration);

        private IEnumerator Fade(float from, float to, float duration)
        {
            if (duration <= 0f) { blackFill.color = new Color(0, 0, 0, to); yield break; }
            float t = 0f;
            while (t < duration)
            {
                float a = Mathf.Lerp(from, to, t / duration);
                blackFill.color = new Color(0, 0, 0, a);
                t += Time.unscaledDeltaTime;
                yield return null;
            }
            blackFill.color = new Color(0, 0, 0, to);
        }
    }
}
