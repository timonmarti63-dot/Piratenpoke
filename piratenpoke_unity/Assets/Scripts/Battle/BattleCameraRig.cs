using System.Collections;
using Unity.Cinemachine;
using UnityEngine;

namespace Piratenpoke.Battle
{
    /// <summary>
    /// Erzeugt zur Laufzeit die drei Kampf-Kameras (Wide / Player-Close / Enemy-Close)
    /// aus Cinemachine 3.x <see cref="CinemachineCamera"/>-Nodes und stellt einen
    /// filmischen Wechsel per Priority zur Verfuegung.
    ///
    /// Wir spawnen die Kameras hier statt sie in der .unity-Szene zu serialisieren,
    /// weil Cinemachine-Component-GUIDs zwischen Package-Versionen wandern koennen —
    /// so bleibt der Setup unabhaengig von der installierten Cinemachine-Version.
    /// </summary>
    [DefaultExecutionOrder(-50)]
    public class BattleCameraRig : MonoBehaviour
    {
        [Header("Ziele (werden vom BattleManager gesetzt)")]
        [SerializeField] private Transform playerTarget;
        [SerializeField] private Transform enemyTarget;

        [Header("Wide-Kamera (Ueberblick)")]
        [SerializeField] private Vector3 wideOffset = new Vector3(0f, 4.5f, -8.5f);
        [SerializeField, Range(20f, 90f)] private float wideFov = 45f;

        [Header("Player-Close (Halbtotale hinter Player, blickt zum Feind)")]
        [SerializeField] private Vector3 playerCloseOffset = new Vector3(-1.6f, 1.9f, -2.8f);
        [SerializeField, Range(20f, 90f)] private float playerCloseFov = 38f;

        [Header("Enemy-Close (Halbtotale hinter Feind, blickt zum Player)")]
        [SerializeField] private Vector3 enemyCloseOffset = new Vector3(1.6f, 1.9f, 2.8f);
        [SerializeField, Range(20f, 90f)] private float enemyCloseFov = 38f;

        [Header("Impact-Kamera (Nahaufnahme auf Getroffenen)")]
        [SerializeField] private Vector3 impactOffset = new Vector3(0.8f, 1.4f, -1.6f);
        [SerializeField, Range(20f, 90f)] private float impactFov = 32f;

        [Header("Blend")]
        [SerializeField, Range(0.05f, 2f)] private float defaultBlendSeconds = 0.6f;
        [SerializeField, Range(0.05f, 1f)] private float impactBlendSeconds = 0.15f;

        public CinemachineCamera CamWide { get; private set; }
        public CinemachineCamera CamPlayer { get; private set; }
        public CinemachineCamera CamEnemy { get; private set; }
        public CinemachineCamera CamImpact { get; private set; }

        private CinemachineBrain _brain;

        public void SetTargets(Transform player, Transform enemy)
        {
            playerTarget = player;
            enemyTarget = enemy;
            RebindTargets();
        }

        public void BuildIfNeeded()
        {
            if (CamWide != null) return;

            // -- CinemachineBrain an der Main Camera sicherstellen
            var mainCam = Camera.main;
            if (mainCam != null)
            {
                _brain = mainCam.GetComponent<CinemachineBrain>();
                if (_brain == null) _brain = mainCam.gameObject.AddComponent<CinemachineBrain>();
                _brain.DefaultBlend = new CinemachineBlendDefinition(
                    CinemachineBlendDefinition.Styles.EaseInOut, defaultBlendSeconds);
            }

            // -- Kameras erzeugen. Priority < 10 = inaktiv, aktive Kamera bekommt 20.
            CamWide = CreateCam("CM_Wide", wideFov, 10);
            CamPlayer = CreateCam("CM_PlayerClose", playerCloseFov, 10);
            CamEnemy = CreateCam("CM_EnemyClose", enemyCloseFov, 10);
            CamImpact = CreateCam("CM_Impact", impactFov, 10);

            RebindTargets();
        }

        private CinemachineCamera CreateCam(string label, float fov, int priority)
        {
            var go = new GameObject(label);
            go.transform.SetParent(transform, false);
            var cam = go.AddComponent<CinemachineCamera>();
            cam.Priority = priority;
            cam.Lens = LensSettings.Default;
            var lens = cam.Lens;
            lens.FieldOfView = fov;
            cam.Lens = lens;
            return cam;
        }

        private void RebindTargets()
        {
            if (playerTarget == null || enemyTarget == null) return;
            // Mittelpunkt zwischen beiden Kämpfern als virtueller Ankerpunkt
            var arenaCenter = new GameObject("BattleAnchor").transform;
            arenaCenter.SetParent(transform, false);
            arenaCenter.position = (playerTarget.position + enemyTarget.position) * 0.5f;

            SetupWide(CamWide, arenaCenter);
            SetupOverShoulder(CamPlayer, playerTarget, enemyTarget, playerCloseOffset);
            SetupOverShoulder(CamEnemy, enemyTarget, playerTarget, enemyCloseOffset);
            // Impact-Kamera wird erst kurz vor der Wirkung positioniert.
        }

        private void SetupWide(CinemachineCamera cam, Transform anchor)
        {
            if (cam == null) return;
            cam.transform.position = anchor.position + wideOffset;
            cam.transform.LookAt(anchor.position + Vector3.up * 1f);
            cam.Target.TrackingTarget = anchor;
        }

        private void SetupOverShoulder(CinemachineCamera cam, Transform behind, Transform lookAt, Vector3 offset)
        {
            if (cam == null || behind == null || lookAt == null) return;
            // Rechtsvektor bezogen auf die Verbindungslinie zwischen den beiden Kaempfern.
            Vector3 forward = (lookAt.position - behind.position).normalized;
            Vector3 right = Vector3.Cross(Vector3.up, forward);
            Vector3 pos = behind.position + right * offset.x + Vector3.up * offset.y - forward * offset.z;
            cam.transform.position = pos;
            cam.transform.LookAt(lookAt.position + Vector3.up * 1f);
            cam.Target.TrackingTarget = lookAt;
        }

        /// <summary>Positioniert die Impact-Kamera dicht am Getroffenen.</summary>
        public void FocusImpact(Transform victim, Transform attacker)
        {
            if (CamImpact == null || victim == null || attacker == null) return;
            Vector3 forward = (victim.position - attacker.position).normalized;
            Vector3 right = Vector3.Cross(Vector3.up, forward);
            Vector3 pos = victim.position + right * impactOffset.x + Vector3.up * impactOffset.y - forward * impactOffset.z;
            CamImpact.transform.position = pos;
            CamImpact.transform.LookAt(victim.position + Vector3.up * 1.2f);
            CamImpact.Target.TrackingTarget = victim;
        }

        /// <summary>Aktiviert die uebergebene Kamera per Priority-Boost.</summary>
        public void Activate(CinemachineCamera cam, bool fastCut = false)
        {
            if (cam == null) return;
            if (_brain != null)
            {
                _brain.DefaultBlend = new CinemachineBlendDefinition(
                    fastCut ? CinemachineBlendDefinition.Styles.Cut
                            : CinemachineBlendDefinition.Styles.EaseInOut,
                    fastCut ? 0f : defaultBlendSeconds);
            }
            if (CamWide != null) CamWide.Priority = 10;
            if (CamPlayer != null) CamPlayer.Priority = 10;
            if (CamEnemy != null) CamEnemy.Priority = 10;
            if (CamImpact != null) CamImpact.Priority = 10;
            cam.Priority = 20;
        }

        /// <summary>
        /// Kurzer Positional-Shake auf der aktuell aktiven Kamera.
        /// Frame-Rate-unabhaengig, laeuft parallel zu Impact-Blends.
        /// </summary>
        public IEnumerator ShakeActive(float amplitude = 0.15f, float duration = 0.25f)
        {
            var cam = CurrentActive();
            if (cam == null) yield break;
            var tr = cam.transform;
            Vector3 basePos = tr.position;
            float t = 0f;
            while (t < duration)
            {
                float damping = 1f - (t / duration);
                Vector3 offset = new Vector3(
                    (Random.value - 0.5f) * amplitude,
                    (Random.value - 0.5f) * amplitude,
                    (Random.value - 0.5f) * amplitude) * damping;
                tr.position = basePos + offset;
                t += Time.deltaTime;
                yield return null;
            }
            tr.position = basePos;
        }

        public IEnumerator PunchImpact(Transform victim, Transform attacker, float holdSeconds = 0.35f)
        {
            FocusImpact(victim, attacker);
            var previouslyActive = CurrentActive();
            // Impact-Kamera schnell schneiden (Snap), dann zurueckblenden.
            if (_brain != null)
            {
                _brain.DefaultBlend = new CinemachineBlendDefinition(
                    CinemachineBlendDefinition.Styles.Cut, 0f);
            }
            if (CamImpact != null) CamImpact.Priority = 30;
            yield return new WaitForSeconds(impactBlendSeconds);
            yield return new WaitForSeconds(holdSeconds);
            if (CamImpact != null) CamImpact.Priority = 5;
            if (_brain != null)
            {
                _brain.DefaultBlend = new CinemachineBlendDefinition(
                    CinemachineBlendDefinition.Styles.EaseInOut, defaultBlendSeconds);
            }
            if (previouslyActive != null) previouslyActive.Priority = 20;
        }

        private CinemachineCamera CurrentActive()
        {
            CinemachineCamera best = null; int bestP = int.MinValue;
            foreach (var c in new[] { CamWide, CamPlayer, CamEnemy, CamImpact })
            {
                if (c == null) continue;
                if (c.Priority > bestP) { bestP = c.Priority; best = c; }
            }
            return best;
        }
    }
}
