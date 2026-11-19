using System;
using System.Collections;
using UnityEditor;
using UnityEngine;

namespace Wizzard.Editor
{
    // Move a separate tracked point so the player's position and save stay intact.
    public static class BellwakeFieldCheck
    {
        [MenuItem("Wizzard/Validate highroad streaming in Play mode")]
        public static void Validate()
        {
            if (!EditorApplication.isPlaying)
                throw new InvalidOperationException("Start Play mode to exercise Unity resource loading.");
            var prefab = Resources.Load<GameObject>("Bellwake/Rooms/Highroad");
            var root = UnityEngine.Object.Instantiate(prefab, Vector3.up * 6000, Quaternion.identity);
            root.name = "Temporary highroad streaming check";
            var field = root.AddComponent<BellwakeField>();
            field.StartCoroutine(Traverse(root, field));
        }

        static IEnumerator Traverse(GameObject root, BellwakeField field)
        {
            try
            {
                var eye = new GameObject("Field test eye").transform;
                eye.SetParent(root.transform, false);
                var markers = root.GetComponentsInChildren<Transform>();
                var west = Array.Find(markers, t => t.name == "FieldAnchor_0_0").position;
                var east = Array.Find(markers, t => t.name == "FieldAnchor_5_6").position;
                eye.position = west;
                yield return field.Open(west, eye, KeepImportedMaterials, renderer => { });
                var original = Surface(root, "FieldCell_0_0");
                if (original == null || Surface(root, "FieldCell_5_6") != null)
                    throw new InvalidOperationException("Incorrect arrival scenery.");
                field.Follow();
                eye.position = east;
                yield return WaitForSwap(root, "FieldCell_5_6", "FieldCell_0_0");
                if (original != null)
                    throw new InvalidOperationException("Previous regional collider survived retirement.");
                eye.position = west;
                yield return WaitForSwap(root, "FieldCell_0_0", "FieldCell_5_6");
                Debug.Log("Highroad round trip passed. Unity loaded, destroyed and reloaded the regional colliders.");
            }
            finally
            {
                UnityEngine.Object.Destroy(root);
            }
        }

        static IEnumerator KeepImportedMaterials(GameObject prefab) { yield break; }

        static MeshCollider Surface(GameObject root, string name)
        {
            foreach (var collider in root.GetComponentsInChildren<MeshCollider>())
                if (collider.name == name && collider.sharedMesh != null &&
                    collider.gameObject.layer == MeadowWorld.GroundLayer) return collider;
            return null;
        }

        static IEnumerator WaitForSwap(GameObject root, string arrived, string retired)
        {
            float timeout = Time.realtimeSinceStartup + 60;
            while (Surface(root, arrived) == null || Surface(root, retired) != null)
            {
                if (Time.realtimeSinceStartup >= timeout)
                    throw new InvalidOperationException("Timed out loading " + arrived + " and retiring " + retired);
                yield return new WaitForSecondsRealtime(.1f);
            }
            yield return null;
        }
    }
}
