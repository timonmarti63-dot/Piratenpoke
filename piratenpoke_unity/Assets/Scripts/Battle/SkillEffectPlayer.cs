using System.Collections;
using UnityEngine;
using Piratenpoke.Data;

namespace Piratenpoke.Battle
{
    /// <summary>
    /// Runtime-Erzeugung von Skill-Effekten: Slash-Trail, Projectile, Burst,
    /// Heal-Puls und Beam. Alles ohne fertige Prefabs — Particles, Line-
    /// Renderer und Materials werden im Code aufgebaut.
    ///
    /// Ein Aufruf: <c>StartCoroutine(effectPlayer.Play(skill, caster, target))</c>
    /// blockt bis der visuelle Effekt abgeschlossen ist. Der Aufrufer kann
    /// den Impact-Moment separat markieren, damit Kamera + Damage-Popup
    /// synchron laufen.
    /// </summary>
    public class SkillEffectPlayer : MonoBehaviour
    {
        /// <summary>Marker: wann in der Effekt-Timeline der Treffer landet (0..1).</summary>
        public float ImpactRatio { get; private set; }

        public IEnumerator Play(SkillSO skill, Transform caster, Transform target)
        {
            if (skill == null || caster == null || target == null) yield break;
            Color color = ResolveColor(skill);
            float duration = skill.vfxDuration > 0f ? skill.vfxDuration : DefaultDuration(skill.vfx);

            switch (skill.vfx)
            {
                case SkillVfx.Slash:      yield return PlaySlash(caster, target, color, duration); break;
                case SkillVfx.Projectile: yield return PlayProjectile(caster, target, color, duration); break;
                case SkillVfx.Burst:      yield return PlayBurst(target, color, duration); break;
                case SkillVfx.Heal:       yield return PlayHeal(caster, color, duration); break;
                case SkillVfx.Beam:       yield return PlayBeam(caster, target, color, duration); break;
                default:                  yield break;
            }
        }

        // --------------------------------------------------------------------
        // Farb-Aufloesung: SkillSO.vfxColor (falls nicht transparent) sonst Element
        // --------------------------------------------------------------------
        private Color ResolveColor(SkillSO skill)
        {
            if (skill.vfxColor.a > 0.01f) return skill.vfxColor;
            switch (skill.element)
            {
                case Element.Fire:  return new Color(1.0f, 0.45f, 0.15f);
                case Element.Water: return new Color(0.25f, 0.65f, 1.0f);
                case Element.Stone: return new Color(0.65f, 0.55f, 0.35f);
                case Element.Wind:  return new Color(0.7f, 1.0f, 0.75f);
                default:            return Color.white;
            }
        }

        private float DefaultDuration(SkillVfx vfx) => vfx switch
        {
            SkillVfx.Slash      => 0.35f,
            SkillVfx.Projectile => 0.55f,
            SkillVfx.Burst      => 0.7f,
            SkillVfx.Heal       => 0.9f,
            SkillVfx.Beam       => 0.6f,
            _                   => 0.4f,
        };

        // --------------------------------------------------------------------
        // Slash: Bogen-Trail vom Caster zum Ziel, drei kurze Streifen
        // --------------------------------------------------------------------
        private IEnumerator PlaySlash(Transform caster, Transform target, Color color, float dur)
        {
            ImpactRatio = 0.55f;
            Vector3 origin = caster.position + Vector3.up * 1.0f;
            Vector3 hit = target.position + Vector3.up * 1.1f;
            Vector3 fwd = (hit - origin).normalized;
            Vector3 right = Vector3.Cross(Vector3.up, fwd);

            var slashes = new GameObject[3];
            for (int i = 0; i < 3; i++)
            {
                var go = new GameObject($"Slash_{i}");
                go.transform.position = origin + right * ((i - 1) * 0.2f) + Vector3.up * (i * 0.15f);
                var line = go.AddComponent<LineRenderer>();
                line.material = SharedAdditiveMaterial(color);
                line.startWidth = 0.22f;
                line.endWidth = 0.02f;
                line.positionCount = 8;
                for (int p = 0; p < 8; p++)
                {
                    float t = p / 7f;
                    Vector3 pos = Vector3.Lerp(origin, hit, t)
                                  + right * Mathf.Sin(t * Mathf.PI) * 0.55f
                                  + Vector3.up * Mathf.Sin(t * Mathf.PI) * 0.25f;
                    line.SetPosition(p, pos);
                }
                slashes[i] = go;
            }

            float t0 = 0f;
            while (t0 < dur)
            {
                float k = 1f - (t0 / dur);
                foreach (var s in slashes)
                {
                    if (s == null) continue;
                    var lr = s.GetComponent<LineRenderer>();
                    if (lr != null)
                    {
                        var c = color; c.a = k;
                        lr.startColor = c; lr.endColor = new Color(c.r, c.g, c.b, 0f);
                    }
                }
                t0 += Time.deltaTime;
                yield return null;
            }
            foreach (var s in slashes) if (s != null) Destroy(s);
        }

        // --------------------------------------------------------------------
        // Projectile: kleine Kugel + Trail fliegt zum Ziel
        // --------------------------------------------------------------------
        private IEnumerator PlayProjectile(Transform caster, Transform target, Color color, float dur)
        {
            ImpactRatio = 0.85f;
            Vector3 origin = caster.position + Vector3.up * 1.1f;
            Vector3 hit = target.position + Vector3.up * 1.1f;

            var proj = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            proj.name = "Projectile";
            Destroy(proj.GetComponent<Collider>());
            proj.transform.localScale = Vector3.one * 0.35f;
            proj.transform.position = origin;
            var mr = proj.GetComponent<MeshRenderer>();
            mr.material = SharedAdditiveMaterial(color);

            var trail = proj.AddComponent<TrailRenderer>();
            trail.material = SharedAdditiveMaterial(color);
            trail.startWidth = 0.35f;
            trail.endWidth = 0f;
            trail.time = 0.25f;
            trail.startColor = color;
            trail.endColor = new Color(color.r, color.g, color.b, 0f);

            // -- Halbe Parabel: hoch-drueber-runter
            float flight = dur * 0.85f;
            float t = 0f;
            while (t < flight)
            {
                float k = t / flight;
                Vector3 pos = Vector3.Lerp(origin, hit, k);
                pos.y += Mathf.Sin(k * Mathf.PI) * 1.2f;
                proj.transform.position = pos;
                t += Time.deltaTime;
                yield return null;
            }
            proj.transform.position = hit;

            // -- Kleiner Aufprall-Flash
            yield return PlayBurst(target, color, dur * 0.3f, radius: 0.7f);
            Destroy(proj);
        }

        // --------------------------------------------------------------------
        // Burst: ParticleSystem-Explosion um das Ziel
        // --------------------------------------------------------------------
        private IEnumerator PlayBurst(Transform target, Color color, float dur, float radius = 1.2f)
        {
            ImpactRatio = 0.0f;
            var go = new GameObject("Burst");
            go.transform.position = target.position + Vector3.up * 1.0f;
            var ps = go.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.duration = dur;
            main.loop = false;
            main.startLifetime = dur * 0.9f;
            main.startSpeed = radius * 4f;
            main.startSize = 0.35f;
            main.startColor = color;
            main.gravityModifier = -0.1f;
            main.maxParticles = 120;
            var emission = ps.emission;
            emission.rateOverTime = 0f;
            emission.SetBursts(new[] { new ParticleSystem.Burst(0f, 60) });
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Sphere;
            shape.radius = 0.1f;
            var col = ps.colorOverLifetime;
            col.enabled = true;
            var gradient = new Gradient();
            gradient.SetKeys(
                new[] { new GradientColorKey(color, 0f), new GradientColorKey(color, 1f) },
                new[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(0f, 1f) });
            col.color = gradient;
            var renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.material = SharedAdditiveMaterial(Color.white);
            ps.Play();
            yield return new WaitForSeconds(dur);
            Destroy(go);
        }

        // --------------------------------------------------------------------
        // Heal: aufsteigende Partikel um den Wirker
        // --------------------------------------------------------------------
        private IEnumerator PlayHeal(Transform caster, Color color, float dur)
        {
            ImpactRatio = 0.15f;
            var healColor = color == Color.white ? new Color(0.4f, 1f, 0.55f) : color;
            var go = new GameObject("HealBurst");
            go.transform.position = caster.position + Vector3.up * 0.2f;
            var ps = go.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.duration = dur;
            main.loop = false;
            main.startLifetime = dur * 0.9f;
            main.startSpeed = 0.8f;
            main.startSize = 0.22f;
            main.startColor = healColor;
            main.gravityModifier = -0.4f;
            main.maxParticles = 80;
            var emission = ps.emission;
            emission.rateOverTime = 45f;
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = 0.6f;
            var col = ps.colorOverLifetime;
            col.enabled = true;
            var gradient = new Gradient();
            gradient.SetKeys(
                new[] { new GradientColorKey(healColor, 0f), new GradientColorKey(Color.white, 1f) },
                new[] { new GradientAlphaKey(0.9f, 0f), new GradientAlphaKey(0f, 1f) });
            col.color = gradient;
            var renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.material = SharedAdditiveMaterial(Color.white);
            ps.Play();
            yield return new WaitForSeconds(dur);
            Destroy(go);
        }

        // --------------------------------------------------------------------
        // Beam: Line-Renderer vom Caster zum Ziel, pulsierend
        // --------------------------------------------------------------------
        private IEnumerator PlayBeam(Transform caster, Transform target, Color color, float dur)
        {
            ImpactRatio = 0.5f;
            var go = new GameObject("Beam");
            var line = go.AddComponent<LineRenderer>();
            line.material = SharedAdditiveMaterial(color);
            line.positionCount = 2;
            line.startWidth = 0.25f;
            line.endWidth = 0.25f;

            float t = 0f;
            while (t < dur)
            {
                if (caster == null || target == null) break;
                Vector3 a = caster.position + Vector3.up * 1.1f;
                Vector3 b = target.position + Vector3.up * 1.1f;
                line.SetPosition(0, a);
                line.SetPosition(1, b);
                float pulse = 0.7f + Mathf.Sin(Time.time * 30f) * 0.3f;
                var c = color; c.a = Mathf.Clamp01((1f - t / dur) * pulse + 0.3f);
                line.startColor = c;
                line.endColor = c;
                line.startWidth = 0.25f + Mathf.Sin(Time.time * 20f) * 0.05f;
                line.endWidth = line.startWidth;
                t += Time.deltaTime;
                yield return null;
            }
            Destroy(go);
        }

        // --------------------------------------------------------------------
        // Shared additive Sprites-Default (haben wir nicht). Wir bauen einfaches
        // additives Material zur Laufzeit ueber den Sprites/Default-Shader.
        // --------------------------------------------------------------------
        private static Material _sharedMat;
        private Material SharedAdditiveMaterial(Color tint)
        {
            // Sprites/Default liegt in allen Unity-Projekten. Wir kopieren pro Tint
            // damit sich Farben nicht ueberschreiben. Ohne Additive Blend Modus,
            // aber mit Tint und Alpha reicht das fuer sichtbare Beams/Slashes.
            var shader = Shader.Find("Sprites/Default");
            if (shader == null) shader = Shader.Find("Unlit/Color");
            var mat = new Material(shader);
            mat.color = tint;
            return mat;
        }
    }
}
