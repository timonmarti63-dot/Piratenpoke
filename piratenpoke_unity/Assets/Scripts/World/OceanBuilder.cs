using Unity.Cinemachine;
using UnityEngine;
using UnityEngine.InputSystem;
using Piratenpoke.SceneManagement;

namespace Piratenpoke.World
{
    /// <summary>
    /// Baut die Ocean-Scene bei Bedarf zur Laufzeit auf: Wasser-Plane mit
    /// Wellen-Modifier, Skybox-Farben, drei Insel-Silhouetten mit
    /// Dock-Triggern, das Spieler-Schiff und eine Cinemachine-Kamera.
    ///
    /// So bleibt das statische .unity-YAML klein und wir sind unabhaengig
    /// von Cinemachine-Package-GUIDs (siehe BattleCameraRig).
    /// </summary>
    public class OceanBuilder : MonoBehaviour
    {
        [Header("Ozean")]
        [SerializeField, Range(60f, 500f)] private float oceanSize = 200f;
        [SerializeField] private Color waterColor = new Color(0.06f, 0.25f, 0.45f, 1f);
        [SerializeField] private Color skyColor = new Color(0.6f, 0.78f, 0.95f, 1f);
        [SerializeField] private Color fogColor = new Color(0.5f, 0.7f, 0.9f, 1f);

        [Header("Schiff")]
        [SerializeField] private Vector3 shipStart = new Vector3(0f, 0.5f, 0f);

        [Header("Kamera")]
        [SerializeField] private Vector3 camOffset = new Vector3(0f, 5f, -9f);
        [SerializeField, Range(20f, 80f)] private float camFov = 55f;

        private void Awake()
        {
            BuildSkyAndFog();
            BuildOceanPlane();
            BuildIslands();
            var ship = BuildShip();
            BuildFollowCamera(ship.transform);
            BuildLight();
        }

        // -----------------------------------------------------------------
        private void BuildSkyAndFog()
        {
            RenderSettings.fog = true;
            RenderSettings.fogColor = fogColor;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogDensity = 0.008f;
            RenderSettings.ambientSkyColor = skyColor;
            Camera.main?.gameObject.SetActive(true);
        }

        private void BuildOceanPlane()
        {
            var plane = GameObject.CreatePrimitive(PrimitiveType.Plane);
            plane.name = "OceanSurface";
            plane.transform.SetParent(transform, false);
            // Standard-Plane ist 10x10 -> auf oceanSize skalieren
            plane.transform.localScale = new Vector3(oceanSize / 10f, 1f, oceanSize / 10f);
            plane.transform.position = Vector3.zero;
            Destroy(plane.GetComponent<MeshCollider>());
            var mr = plane.GetComponent<MeshRenderer>();
            var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            var mat = new Material(shader);
            mat.color = waterColor;
            if (mat.HasProperty("_Smoothness")) mat.SetFloat("_Smoothness", 0.75f);
            if (mat.HasProperty("_Metallic"))   mat.SetFloat("_Metallic", 0.1f);
            mr.material = mat;
            plane.AddComponent<OceanWaves>();
        }

        private void BuildLight()
        {
            var sunGo = new GameObject("SunLight");
            sunGo.transform.SetParent(transform, false);
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.96f, 0.88f);
            sun.intensity = 1.2f;
            sunGo.transform.rotation = Quaternion.Euler(48f, -30f, 0f);
        }

        // -----------------------------------------------------------------
        private void BuildIslands()
        {
            // Drei Inseln in einem Dreieck um Origin. Alle laden aktuell dieselbe
            // TestIsland-Scene; Sprint 4 verteilt echte Ziele.
            CreateIsland("Isle_Kelpholm",  new Vector3(-40f, 0f,  35f), 12f,
                new Color(0.6f, 0.7f, 0.35f), SceneTunnel.TargetScene.Village);
            CreateIsland("Isle_TestBucht", new Vector3( 42f, 0f,  20f), 15f,
                new Color(0.55f, 0.75f, 0.45f), SceneTunnel.TargetScene.Overworld);
            CreateIsland("Isle_Vulkan",    new Vector3(  8f, 0f, -55f), 18f,
                new Color(0.5f, 0.35f, 0.3f), SceneTunnel.TargetScene.Overworld);
        }

        private void CreateIsland(string label, Vector3 pos, float radius, Color color,
                                  SceneTunnel.TargetScene target)
        {
            // Insel-Kern: Zylinder (flach), leicht ueber Wasser
            var isle = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            isle.name = label;
            isle.transform.SetParent(transform, false);
            isle.transform.position = pos + Vector3.up * 0.3f;
            isle.transform.localScale = new Vector3(radius, 0.6f, radius);
            var mr = isle.GetComponent<MeshRenderer>();
            var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            var mat = new Material(shader);
            mat.color = color;
            mr.material = mat;
            // Collider bleibt (Standard-CapsuleCollider vom Primitive)

            // Kleine Palme (Cube) obendrauf als Deko
            var palm = GameObject.CreatePrimitive(PrimitiveType.Cube);
            palm.name = $"{label}_Landmark";
            palm.transform.SetParent(isle.transform, false);
            palm.transform.localPosition = new Vector3(0f, 1.5f, 0f);
            palm.transform.localScale = new Vector3(0.2f, 3f, 0.2f) * (1f / radius);
            Destroy(palm.GetComponent<BoxCollider>());
            var palmMr = palm.GetComponent<MeshRenderer>();
            var palmMat = new Material(shader);
            palmMat.color = new Color(0.4f, 0.25f, 0.15f);
            palmMr.material = palmMat;

            // Dock-Trigger: dicker Ring um die Insel, laed die Ziel-Scene
            var dockGo = new GameObject($"{label}_Dock");
            dockGo.transform.SetParent(transform, false);
            dockGo.transform.position = pos;
            var dockCol = dockGo.AddComponent<SphereCollider>();
            dockCol.isTrigger = true;
            dockCol.radius = radius * 1.4f;
            var tunnel = dockGo.AddComponent<SceneTunnel>();
            var targetField = typeof(SceneTunnel).GetField("target",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            if (targetField != null) targetField.SetValue(tunnel, target);
        }

        // -----------------------------------------------------------------
        private GameObject BuildShip()
        {
            // Wurzel: Rigidbody + Ship-Controller + Collider
            var root = new GameObject("PlayerShip");
            root.tag = "Player";
            root.transform.SetParent(transform, false);
            root.transform.position = shipStart;
            var rb = root.AddComponent<Rigidbody>();
            rb.mass = 3f;
            var col = root.AddComponent<CapsuleCollider>();
            col.direction = 2; // Z-Achse (laengs)
            col.center = Vector3.zero;
            col.radius = 0.9f;
            col.height = 4.5f;

            // Sichtbarer Rumpf (fuer Roll-Animation)
            var hull = new GameObject("HullVisual");
            hull.transform.SetParent(root.transform, false);
            hull.transform.localPosition = Vector3.zero;

            // Rumpf-Body (langer Cube, gestreckt)
            var body = GameObject.CreatePrimitive(PrimitiveType.Cube);
            body.name = "Hull";
            body.transform.SetParent(hull.transform, false);
            body.transform.localPosition = new Vector3(0f, 0.1f, 0f);
            body.transform.localScale = new Vector3(1.4f, 0.7f, 4.2f);
            Destroy(body.GetComponent<BoxCollider>());
            PaintPrimitive(body, new Color(0.45f, 0.28f, 0.15f));

            // Kabinen-Aufbau
            var cabin = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cabin.name = "Cabin";
            cabin.transform.SetParent(hull.transform, false);
            cabin.transform.localPosition = new Vector3(0f, 0.9f, -0.6f);
            cabin.transform.localScale = new Vector3(1.0f, 0.7f, 1.4f);
            Destroy(cabin.GetComponent<BoxCollider>());
            PaintPrimitive(cabin, new Color(0.55f, 0.35f, 0.2f));

            // Mast + Segel
            var mast = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            mast.name = "Mast";
            mast.transform.SetParent(hull.transform, false);
            mast.transform.localPosition = new Vector3(0f, 1.6f, 0.5f);
            mast.transform.localScale = new Vector3(0.12f, 1.6f, 0.12f);
            Destroy(mast.GetComponent<CapsuleCollider>());
            PaintPrimitive(mast, new Color(0.3f, 0.2f, 0.12f));

            var sail = GameObject.CreatePrimitive(PrimitiveType.Cube);
            sail.name = "Sail";
            sail.transform.SetParent(hull.transform, false);
            sail.transform.localPosition = new Vector3(0f, 1.8f, 0.5f);
            sail.transform.localScale = new Vector3(1.8f, 1.4f, 0.05f);
            Destroy(sail.GetComponent<BoxCollider>());
            PaintPrimitive(sail, new Color(0.95f, 0.92f, 0.85f));

            // ShipController konfigurieren
            var ship = root.AddComponent<ShipController>();
            var hullField = typeof(ShipController).GetField("hullVisual",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            if (hullField != null) hullField.SetValue(ship, hull.transform);

            // PlayerInput fuer WASD-Bewegung (nutzt Send Messages).
            // Wir haengen es an, das Actions-Asset wird zur Laufzeit nicht
            // gebraucht -- ShipController hat einen Input-Fallback ueber die
            // Legacy Axes.
            var pi = root.AddComponent<PlayerInput>();
            pi.notificationBehavior = PlayerNotifications.SendMessages;

            return root;
        }

        private void PaintPrimitive(GameObject go, Color color)
        {
            var mr = go.GetComponent<MeshRenderer>();
            var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            var mat = new Material(shader);
            mat.color = color;
            mr.material = mat;
        }

        // -----------------------------------------------------------------
        private void BuildFollowCamera(Transform ship)
        {
            var mainCam = Camera.main;
            if (mainCam == null)
            {
                var camGo = new GameObject("Main Camera");
                camGo.tag = "MainCamera";
                camGo.transform.SetParent(transform, false);
                camGo.AddComponent<Camera>();
                camGo.AddComponent<AudioListener>();
                mainCam = camGo.GetComponent<Camera>();
            }
            mainCam.backgroundColor = skyColor;
            mainCam.clearFlags = CameraClearFlags.SolidColor;
            mainCam.farClipPlane = 800f;

            var brain = mainCam.GetComponent<CinemachineBrain>();
            if (brain == null) brain = mainCam.gameObject.AddComponent<CinemachineBrain>();

            var camRigGo = new GameObject("ShipFollowCam");
            camRigGo.transform.SetParent(transform, false);
            var cmCam = camRigGo.AddComponent<CinemachineCamera>();
            cmCam.Priority = 20;
            var lens = LensSettings.Default;
            lens.FieldOfView = camFov;
            lens.FarClipPlane = 800f;
            cmCam.Lens = lens;
            cmCam.Target.TrackingTarget = ship;

            var follow = camRigGo.AddComponent<CinemachineFollow>();
            follow.FollowOffset = camOffset;

            var composer = camRigGo.AddComponent<CinemachineRotationComposer>();
            composer.TargetOffset = new Vector3(0f, 1.2f, 0f);
        }
    }
}
