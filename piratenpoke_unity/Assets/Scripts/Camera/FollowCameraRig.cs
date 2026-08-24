using Unity.Cinemachine;
using UnityEngine;

namespace Piratenpoke.CameraSystem
{
    /// <summary>
    /// Legt zur Laufzeit ein Cinemachine 3.x Follow-Rig an, wenn keins existiert.
    /// So kann die Testinsel-Scene ohne manuelle Editor-Konfiguration laufen --
    /// im Editor kann man das Prefab spaeter durch ein handkonfiguriertes
    /// CinemachineCamera-Objekt ersetzen.
    ///
    /// Winkel & Distanz wie in Pokemon Sw/Sh: leicht ueber Kopfhoehe, sanfter
    /// Nachlauf.
    /// </summary>
    public class FollowCameraRig : MonoBehaviour
    {
        [Header("Ziel")]
        [SerializeField] private Transform followTarget;

        [Header("Rig-Parameter")]
        [SerializeField] private Vector3 offset = new Vector3(0f, 3.5f, -6f);
        [SerializeField, Range(0f, 10f)] private float followDamping = 1.2f;
        [SerializeField, Range(0f, 10f)] private float rotationDamping = 0.8f;

        private CinemachineCamera _cam;

        private void Awake()
        {
            if (followTarget == null)
            {
                var p = GameObject.FindGameObjectWithTag("Player");
                if (p != null) followTarget = p.transform;
            }
        }

        private void Start()
        {
            _cam = GetComponentInChildren<CinemachineCamera>();
            if (_cam == null) BuildRig();
            else ApplyTarget();
        }

        private void BuildRig()
        {
            var go = new GameObject("PlayerFollowCam");
            go.transform.SetParent(transform, false);
            _cam = go.AddComponent<CinemachineCamera>();

            var follow = go.AddComponent<CinemachineFollow>();
            follow.FollowOffset = offset;
            follow.TrackerSettings.PositionDamping = new Vector3(followDamping, followDamping, followDamping);
            follow.TrackerSettings.RotationDamping = new Vector3(rotationDamping, rotationDamping, rotationDamping);

            var aim = go.AddComponent<CinemachineRotationComposer>();
            aim.Composition.ScreenPosition = new Vector2(0f, 0.15f); // leicht ueber Bildmitte
            aim.Damping = new Vector2(0.5f, 0.5f);

            ApplyTarget();
        }

        private void ApplyTarget()
        {
            if (_cam == null || followTarget == null) return;
            _cam.Target.TrackingTarget = followTarget;
            _cam.Target.LookAtTarget = followTarget;
        }
    }
}
