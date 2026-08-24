using UnityEngine;
using Piratenpoke.Data;
using Piratenpoke.SceneManagement;

namespace Piratenpoke.Encounter
{
    /// <summary>
    /// Ein sichtbarer 3D-Gegner in der Overworld.
    ///
    /// * Patrouilliert zwischen zwei Punkten (waypointA / waypointB)
    /// * Trigger-Collider: Beruehrung durch Player laedt die Battle-Scene mit
    ///   der zugewiesenen EnemyData
    /// * Visualisierung: Capsule mit Farbe = enemyData.placeholderColor
    ///
    /// Muss auf einem GameObject mit CapsuleCollider (isTrigger) liegen.
    /// </summary>
    [RequireComponent(typeof(CapsuleCollider))]
    public class EnemyPatrol : MonoBehaviour
    {
        [Header("Daten")]
        public EnemyDataSO enemyData;

        [Header("Patrouille")]
        public Transform waypointA;
        public Transform waypointB;
        [SerializeField, Min(0f)] private float moveSpeed = 1.6f;
        [SerializeField, Min(0f)] private float pauseAtWaypoint = 1.0f;

        [Header("Visualisierung")]
        [SerializeField] private MeshRenderer capsuleRenderer;

        private Vector3 _startA, _startB;
        private Vector3 _target;
        private float _pauseTimer;
        private bool _defeated;

        private void Awake()
        {
            _startA = waypointA != null ? waypointA.position : transform.position - transform.right * 3f;
            _startB = waypointB != null ? waypointB.position : transform.position + transform.right * 3f;
            _target = _startB;

            if (capsuleRenderer != null && enemyData != null)
                capsuleRenderer.material.color = enemyData.placeholderColor;
        }

        private void Update()
        {
            if (_defeated) return;

            if (_pauseTimer > 0f)
            {
                _pauseTimer -= Time.deltaTime;
                return;
            }

            Vector3 toTarget = _target - transform.position;
            toTarget.y = 0f;
            if (toTarget.sqrMagnitude < 0.05f)
            {
                _pauseTimer = pauseAtWaypoint;
                _target = (_target == _startA) ? _startB : _startA;
                return;
            }

            Vector3 step = toTarget.normalized * moveSpeed * Time.deltaTime;
            transform.position += step;
            transform.rotation = Quaternion.Slerp(transform.rotation,
                Quaternion.LookRotation(toTarget), 8f * Time.deltaTime);
        }

        private void OnTriggerEnter(Collider other)
        {
            if (_defeated) return;
            if (!other.CompareTag("Player")) return;
            if (enemyData == null)
            {
                Debug.LogWarning($"EnemyPatrol {name}: enemyData ist leer.", this);
                return;
            }

            _defeated = true;
            BattleContext.PendingEnemy = enemyData;
            BattleContext.PendingSourcePatrol = this;
            SceneRouter.Instance?.EnterBattle();
        }

        /// <summary>Nach gewonnenem Kampf: entfernt sich (oder respawnt).</summary>
        public void OnBattleWon()
        {
            gameObject.SetActive(false);
        }

        /// <summary>Nach Flucht: patrouilliert weiter, aber pausiert kurz.</summary>
        public void OnPlayerFled()
        {
            _defeated = false;
            _pauseTimer = 2.5f;
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.red;
            if (waypointA != null && waypointB != null)
                Gizmos.DrawLine(waypointA.position, waypointB.position);
        }
    }
}
