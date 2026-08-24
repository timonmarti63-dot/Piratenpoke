using UnityEngine;
using UnityEngine.InputSystem;

namespace Piratenpoke.Player
{
    /// <summary>
    /// 3D-Spielersteuerung im Switch-Pokemon-Stil.
    ///
    /// * WASD / linker Analogstick: 360-Grad-Bewegung relativ zur Kamera
    /// * Space / Sued-Button: kurzer Sprung
    /// * E / West-Button: Interaktion (Raycast nach vorne, s. InteractionRaycaster)
    ///
    /// Nutzt Unitys standard <see cref="CharacterController"/> (Kinematic).
    /// Die Follow-Camera ist ein separater Cinemachine CamerBrain; siehe
    /// FollowCameraRig.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerController3D : MonoBehaviour
    {
        [Header("Bewegung")]
        [SerializeField, Min(0f)] private float walkSpeed = 5f;
        [SerializeField, Min(0f)] private float runSpeedMultiplier = 1.6f;
        [SerializeField, Range(1f, 30f)] private float rotationSpeed = 12f;
        [SerializeField] private float gravity = -20f;
        [SerializeField, Min(0f)] private float jumpHeight = 1.2f;

        [Header("Referenzen")]
        [SerializeField] private Transform cameraTransform;

        [Header("Debug")]
        [SerializeField] private bool logMovement = false;

        private CharacterController _controller;
        private Vector2 _moveInput;
        private bool _runHeld;
        private bool _jumpQueued;
        private Vector3 _verticalVelocity;

        // -- Input-System-Bindings (werden von PlayerInput per SendMessage aufgerufen)
        public void OnMove(InputValue value) => _moveInput = value.Get<Vector2>();
        public void OnRun(InputValue value) => _runHeld = value.isPressed;
        public void OnJump(InputValue value)
        {
            if (value.isPressed && _controller != null && _controller.isGrounded)
                _jumpQueued = true;
        }

        private void Awake()
        {
            _controller = GetComponent<CharacterController>();
            if (cameraTransform == null && Camera.main != null)
                cameraTransform = Camera.main.transform;
        }

        private void Update()
        {
            // -- Planare Bewegung relativ zur Kamera (Switch-Feeling)
            Vector3 planarInput = new Vector3(_moveInput.x, 0f, _moveInput.y);
            Vector3 worldMove = Vector3.zero;

            if (planarInput.sqrMagnitude > 0.001f && cameraTransform != null)
            {
                Vector3 fwd = cameraTransform.forward;
                Vector3 right = cameraTransform.right;
                fwd.y = 0f; right.y = 0f;
                fwd.Normalize(); right.Normalize();
                worldMove = fwd * planarInput.z + right * planarInput.x;
                if (worldMove.sqrMagnitude > 1f) worldMove.Normalize();

                // Sanfte Rotation zur Laufrichtung
                Quaternion target = Quaternion.LookRotation(worldMove);
                transform.rotation = Quaternion.Slerp(
                    transform.rotation, target, rotationSpeed * Time.deltaTime);
            }

            float speed = walkSpeed * (_runHeld ? runSpeedMultiplier : 1f);
            Vector3 velocity = worldMove * speed;

            // -- Schwerkraft / Sprung
            if (_controller.isGrounded)
            {
                _verticalVelocity.y = -1f; // sanft am Boden halten
                if (_jumpQueued)
                {
                    _verticalVelocity.y = Mathf.Sqrt(-2f * gravity * jumpHeight);
                    _jumpQueued = false;
                }
            }
            else
            {
                _verticalVelocity.y += gravity * Time.deltaTime;
            }
            velocity.y = _verticalVelocity.y;

            _controller.Move(velocity * Time.deltaTime);

            if (logMovement && worldMove.sqrMagnitude > 0.01f)
                Debug.Log($"Player move: {worldMove:F2} speed={speed:F1}");
        }
    }
}
