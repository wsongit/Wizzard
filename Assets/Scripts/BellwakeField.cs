using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Wizzard
{
    public sealed class BellwakeField : MonoBehaviour
    {
        // Scenery extends up to 110 m beyond its survey marker. Warm it well before contact.
        const float LoadRadius = 365, ReleaseRadius = 425;
        sealed class Cell
        {
            public string resource;
            public Vector3 centre;
            public GameObject instance;
        }
        readonly List<Cell> cells = new List<Cell>();
        public int LoadedCells { get; private set; }
        public int RetiredCells { get; private set; }
        public int CompletedSweeps { get; private set; }

        int retiredSinceSweep;
        float lastSweep;
        Transform eye;
        Func<GameObject, IEnumerator> loadPaints;
        Action<Renderer> paint;

        public IEnumerator Open(Vector3 arrival, Transform head, Func<GameObject, IEnumerator> prepare,
                                Action<Renderer> apply)
        {
            eye = head;
            lastSweep = Time.realtimeSinceStartup;
            loadPaints = prepare;
            paint = apply;
            foreach (Transform mark in GetComponentsInChildren<Transform>())
            {
                if (!mark.name.StartsWith("FieldAnchor_", StringComparison.Ordinal)) continue;
                cells.Add(new Cell {
                    centre = mark.position,
                    resource = "Bellwake/Field/" + mark.name.Replace("FieldAnchor_", "FieldCell_")
                });
            }
            if (cells.Count != 42) throw new InvalidOperationException("Incomplete watershed field anchors");
            yield return Refresh(arrival);
        }

        public void Follow()
        {
            StartCoroutine(Track());
        }

        IEnumerator Track()
        {
            Vector3 last = eye.position;
            var interval = new WaitForSecondsRealtime(.35f);
            while (true)
            {
                yield return interval;
                if ((eye.position - last).sqrMagnitude < 100)
                {
                    if (retiredSinceSweep > 0 && Time.realtimeSinceStartup - lastSweep > 12)
                        yield return Sweep();
                    continue;
                }
                last = eye.position;
                yield return Refresh(last);
            }
        }

        IEnumerator Refresh(Vector3 position)
        {
            foreach (var cell in cells)
            {
                if (cell.instance == null || (cell.centre-position).sqrMagnitude <= ReleaseRadius*ReleaseRadius)
                    continue;
                cell.instance.SetActive(false);
                Destroy(cell.instance);
                cell.instance = null;
                retiredSinceSweep++;
                RetiredCells++;
            }
            // Nearest first so a restored checkpoint always has hand contacts when the fade opens.
            cells.Sort((a,b) => (a.centre-position).sqrMagnitude.CompareTo((b.centre-position).sqrMagnitude));
            foreach (var cell in cells)
            {
                if (cell.instance != null || (cell.centre-position).sqrMagnitude > LoadRadius*LoadRadius)
                    continue;
                var request = Resources.LoadAsync<GameObject>(cell.resource);
                yield return request;
                var prefab = request.asset as GameObject;
                if (prefab == null) throw new InvalidOperationException("Missing field scenery " + cell.resource);
                yield return loadPaints(prefab);
                cell.instance = Instantiate(prefab, transform, false);
                LoadedCells++;
                foreach (var renderer in cell.instance.GetComponentsInChildren<MeshRenderer>()) paint(renderer);
            }
            // Batch global sweeps on long walks. Retired colliders disappear immediately.
            if (retiredSinceSweep >= 8) yield return Sweep();
        }

        IEnumerator Sweep()
        {
            yield return null;
            yield return Resources.UnloadUnusedAssets();
            CompletedSweeps++;
            retiredSinceSweep = 0;
            lastSweep = Time.realtimeSinceStartup;
        }
    }
}
