using UnityEngine;

namespace Piratenpoke.World
{
    /// <summary>
    /// Rigidbody-basierter Schiffs-Controller mit Beschleunigung/Wende + Drift.
    /// W/S = vor/zurueck, A/D = Ruder. Nutzt SendMessage-Interface vom PlayerInput
    /// wie der Landkarten-Controller, damit die gleichen Input-Actions
    /// (Move, Interact) wiederverwendet werden koennen.
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    public class ShipController : MonoBehaviour
    {
        [Header("Fahrverhalten")]
        [SerializeField, Range(1f, 20f)] private float thrustForce = 8f;
        [SerializeField, Range(0.5f, 15f)] private float reverseFactor = 0.4f;
        [SerializeField, Range(10f, 120f)] private float turnSpeedDeg = 55f;
        [SerializeField, Range(0.5f, 10f)] private float linearDrag = 1.8f;
        [SerializeField, Range(0.5f, 10f)] private float angularDrag = 3.5f;
        [SerializeField, Range(1f, 30f)]   private float maxSpeed = 12f;

        [Header("Optik")]
        [Tooltip("Sichtbarer Rumpf; wird leicht geneigt bei Wende.")]
        [SerializeField] private Transform hullVisual;
        [SerializeField, Range(0f, 25f)] private float rollAmountDeg = 8f;
        [SerializeField, Range(0.5f, 8f)] private float rollLerp = 3f;

        private Rigidbody _rb;
        private Vector2 _move; // x = turn (A/D), y = thrust (W/S)
        private float _currentRoll;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _rb.useGravity = false;   // Ozean-Ebene, wir halten y konstant
            _rb.linearDamping = linearDrag;
            _rb.angularDamping = angularDrag;
            _rb.constraints = RigidbodyConstraints.FreezePositionY
                            | RigidbodyConstraints.FreezeRotationX
                            | RigidbodyConstraints.FreezeRotationZ;
        }

        // Vom PlayerInput per SendMessage-Interface aufgerufen.
        public void OnMove(UnityEngine.InputSystem.InputValue v) => _move = v.Get<Vector2>();

        // Fallback fuer Setup ohne Input-Actions-Asset.
        private void Update()
        {
            if (Mathf.Abs(_move.x) + Mathf.Abs(_move.y) < 0.001f)
            {
                float h = Input.GetAxisRaw("Horizontal");
                float v = Input.GetAxisRaw("Vertical");
                _move = new Vector2(h, v);
            }
            UpdateRoll();
        }

        private void FixedUpdate()
        {
            // Wende: nur rotieren wenn wir ueberhaupt Fahrt haben (kein Wenden auf der Stelle).
            float speed = _rb.linearVelocity.magnitude;
            float turnGain = Mathf.Clamp01(speed / (maxSpeed * 0.5f)) + 0.15f;
            if (Mathf.Abs(_move.x) > 0.01f)
            {
                float yaw = _move.x * turnSpeedDeg * turnGain * Time.fixedDeltaTime;
                _rb.MoveRotation(_rb.rotation * Quaternion.Euler(0f, yaw, 0f));
            }

            // Schub: vor = _move.y > 0, zurueck = _move.y < 0 (schwaecher)
            if (Mathf.Abs(_move.y) > 0.01f)
            {
                float factor = _move.y > 0f ? 1f : reverseFactor;
                Vector3 push = transform.forward * (_move.y * thrustForce * factor);
                _rb.AddForce(push, ForceMode.Acceleration);
            }

            // Max-Speed kappen
            if (_rb.linearVelocity.magnitude > maxSpeed)
                _rb.linearVelocity = _rb.linearVelocity.normalized * maxSpeed;
        }

        private void UpdateRoll()
        {
            if (hullVisual == null) return;
            float targetRoll = -_move.x * rollAmountDeg;
            _currentRoll = Mathf.Lerp(_currentRoll, targetRoll, Time.deltaTime * rollLerp);
            var e = hullVisual.localEulerAngles;
            hullVisual.localEulerAngles = new Vector3(e.x, e.y, _currentRoll);
        }
    }
}
