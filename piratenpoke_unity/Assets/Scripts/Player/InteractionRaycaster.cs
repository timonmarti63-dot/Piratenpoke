using UnityEngine;
using UnityEngine.InputSystem;

namespace Piratenpoke.Player
{
    /// <summary>
    /// Interface fuer alles, was man mit 'E' beruehren kann:
    /// NPCs, Tueren, Schilder.
    /// </summary>
    public interface IInteractable
    {
        void Interact(PlayerController3D player);
        string PromptText { get; }
    }

    /// <summary>
    /// Schiesst bei 'Interact' einen kurzen Raycast nach vorne und ruft
    /// <see cref="IInteractable.Interact"/> auf, wenn getroffen.
    /// </summary>
    public class InteractionRaycaster : MonoBehaviour
    {
        [SerializeField, Min(0.1f)] private float range = 1.6f;
        [SerializeField, Min(0.1f)] private float sphereRadius = 0.4f;
        [SerializeField] private LayerMask interactableMask = ~0;
        [SerializeField] private Transform originOverride;

        public void OnInteract(InputValue value)
        {
            if (!value.isPressed) return;
            TryInteract();
        }

        private void TryInteract()
        {
            Transform origin = originOverride != null ? originOverride : transform;
            Vector3 pos = origin.position + Vector3.up * 0.6f;
            Vector3 dir = origin.forward;

            if (Physics.SphereCast(pos, sphereRadius, dir, out RaycastHit hit,
                                   range, interactableMask, QueryTriggerInteraction.Collide))
            {
                var interactable = hit.collider.GetComponentInParent<IInteractable>();
                if (interactable != null)
                {
                    var player = GetComponent<PlayerController3D>();
                    interactable.Interact(player);
                }
            }
        }

        private void OnDrawGizmosSelected()
        {
            Transform origin = originOverride != null ? originOverride : transform;
            Gizmos.color = Color.cyan;
            Gizmos.DrawWireSphere(origin.position + Vector3.up * 0.6f + origin.forward * range, sphereRadius);
        }
    }
}
