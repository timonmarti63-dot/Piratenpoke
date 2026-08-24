using UnityEngine;

namespace Piratenpoke.World
{
    /// <summary>
    /// Verschiebt die Vertices eines Meshes zur Laufzeit per Summe zweier
    /// Sinuswellen -- fuehlt sich fuer den Prototyp wie sanfte Duenung an.
    ///
    /// Wird zur Laufzeit an das Ocean-Plane gehaengt (via BootStrap oder
    /// direkt im OceanScene-YAML).
    /// </summary>
    [RequireComponent(typeof(MeshFilter))]
    public class OceanWaves : MonoBehaviour
    {
        [SerializeField, Range(0.05f, 2f)] private float amplitude = 0.35f;
        [SerializeField] private Vector2 waveA = new Vector2(0.25f, 0.10f);
        [SerializeField] private Vector2 waveB = new Vector2(0.12f, 0.30f);
        [SerializeField, Range(0.1f, 5f)] private float speed = 0.8f;

        private Mesh _mesh;
        private Vector3[] _base;
        private Vector3[] _work;

        private void Awake()
        {
            var mf = GetComponent<MeshFilter>();
            // Wir clonen das Mesh damit das Sharedmesh (Unity-Built-in-Plane) unberuehrt bleibt.
            _mesh = Instantiate(mf.sharedMesh);
            mf.mesh = _mesh;
            _base = _mesh.vertices;
            _work = new Vector3[_base.Length];
        }

        private void Update()
        {
            float t = Time.time * speed;
            for (int i = 0; i < _base.Length; i++)
            {
                var v = _base[i];
                float h = Mathf.Sin(v.x * waveA.x + t) * Mathf.Cos(v.z * waveA.y + t * 0.7f);
                h += 0.5f * Mathf.Sin(v.x * waveB.x + t * 1.3f) * Mathf.Cos(v.z * waveB.y + t);
                v.y = h * amplitude;
                _work[i] = v;
            }
            _mesh.vertices = _work;
            _mesh.RecalculateNormals();
        }
    }
}
