using System.Collections;
using UnityEngine;
using TMPro;

namespace Piratenpoke.Battle
{
    /// <summary>
    /// World-Space-Zahl, die vom Getroffenen aufsteigt und ausblendet.
    /// Wird zur Laufzeit erzeugt.
    /// </summary>
    public static class DamagePopup
    {
        public static Coroutine Show(MonoBehaviour host, Transform victim, int amount, Color color, bool crit = false)
        {
            if (host == null || victim == null) return null;
            return host.StartCoroutine(Run(victim, amount, color, crit));
        }

        public static Coroutine ShowText(MonoBehaviour host, Transform victim, string text, Color color)
        {
            if (host == null || victim == null) return null;
            return host.StartCoroutine(RunText(victim, text, color));
        }

        private static IEnumerator Run(Transform victim, int amount, Color color, bool crit)
        {
            string s = crit ? $"-{amount}!" : $"-{amount}";
            yield return RunText(victim, s, color);
        }

        private static IEnumerator RunText(Transform victim, string text, Color color)
        {
            var go = new GameObject("DmgPopup");
            go.transform.position = victim.position + Vector3.up * 1.9f;

            var canvasGo = new GameObject("Canvas");
            canvasGo.transform.SetParent(go.transform, false);
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.WorldSpace;
            canvas.sortingOrder = 100;
            var rt = canvas.GetComponent<RectTransform>();
            rt.sizeDelta = new Vector2(2f, 1f);
            rt.localScale = Vector3.one * 0.02f;

            var tmpGo = new GameObject("Text");
            tmpGo.transform.SetParent(canvasGo.transform, false);
            var tmp = tmpGo.AddComponent<TextMeshProUGUI>();
            tmp.text = text;
            tmp.alignment = TextAlignmentOptions.Center;
            tmp.fontSize = 48;
            tmp.color = color;
            tmp.enableWordWrapping = false;
            tmp.fontStyle = FontStyles.Bold;
            var tmpRt = tmp.GetComponent<RectTransform>();
            tmpRt.sizeDelta = new Vector2(400, 100);

            float t = 0f, dur = 1.0f;
            Vector3 start = go.transform.position;
            while (t < dur)
            {
                if (Camera.main != null)
                {
                    go.transform.rotation = Quaternion.LookRotation(
                        go.transform.position - Camera.main.transform.position);
                }
                float k = t / dur;
                go.transform.position = start + Vector3.up * (k * 1.2f);
                float scale = 1f + Mathf.Sin(k * Mathf.PI) * 0.4f;
                canvasGo.transform.localScale = Vector3.one * 0.02f * scale;
                var c = color; c.a = 1f - k * k;
                tmp.color = c;
                t += Time.deltaTime;
                yield return null;
            }
            Object.Destroy(go);
        }
    }
}
