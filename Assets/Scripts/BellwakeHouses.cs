using System;
using System.Collections.Generic;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Wizzard
{
// The room mesh and address register are exported from the same Blender sources as the browser game.
public sealed class BellwakeHouses
{
    [Serializable]
    public class Address
    {
        public float[] point, normal;
        public string layout, name, objectName, lore;
        public int sign;
        public bool paintDoor, openSpace, millPassage;
        [NonSerialized]
        public Vector3 position, outward;
    }
    [Serializable]
    class Anchor
    {
        public string name;
        public float[] p;
    }
    [Serializable]
    class District
    {
        public string key;
        public Anchor[] anchors;
        public Address[] doors;
    }
    [Serializable]
    class Register
    {
        public District[] districts;
        public string[] signs;
    }
    [Serializable]
    class Shell
    {
        public float[] pos, uv, light;
        public int[] indices;
    }
    const string Path = "Bellwake/Houses/";
    readonly GorillaPlayer player;
    readonly BellwakeDisplay display;
    readonly Register register;
    readonly Vector3 roomOrigin = new Vector3(0, 1600, 0);
    readonly List<Mesh> boardMeshes = new List<Mesh>();
    readonly List<Material> boardMaterials = new List<Material>();
    Address[] doors = Array.Empty<Address>();
    GameObject boards, room;
    Mesh roomMesh;
    Material roomMaterial;
    Address active, notice;
    bool reading;
    string caption, captionTitle;
    Vector3 returnFeet;
    Quaternion returnFacing;
    public bool Inside => active != null;
    public BellwakeHouses(GorillaPlayer rig, BellwakeDisplay hud)
    {
        player = rig;
        display = hud;
        register = JsonUtility.FromJson<Register>(Resources.Load<TextAsset>(Path + "Addresses").text);
    }
    static Vector3 V(float[] p) => new Vector3(p[0], p[1], p[2]);
    static Vector3 Local(float x, float y, float z) => new Vector3(x, y, -z);
    Material Paint(string file)
    {
        var m = new Material(Shader.Find("Wizzard/HousePaint"));
        m.mainTexture = Resources.Load<Texture2D>(Path + file);
        return m;
    }
    public void Bind(string key, Dictionary<string, Transform> nodes, Transform parent)
    {
        Clear();
        var area = Array.Find(register.districts, d => d.key == key);
        if (area == null)
            return;
        var a = area.anchors;
        Vector3 p = V(a[0].p), b = V(a[1].p) - p, c = V(a[2].p) - p;
        Vector3 origin = nodes[a[0].name].position, bx = nodes[a[1].name].position - origin,
                cx = nodes[a[2].name].position - origin;
        bx.y = cx.y = 0;
        float det = b.x * c.z - c.x * b.z;
        Vector3 Map(Vector3 q)
        {
            var d = q - p;
            return origin + bx * ((d.x * c.z - d.z * c.x) / det) + cx * ((b.x * d.z - b.z * d.x) / det) +
                   Vector3.up * d.y;
        }
        Fit(area, parent, Map);
    }
    public void BindVillage(Transform parent, Vector3 arrival, Vector3 east, Vector3 forward)
    {
        Clear();
        var area = Array.Find(register.districts, d => d.key == "MossbellVillage");
        Fit(area, parent, q => arrival + east * q.x - forward * (q.z - 21f) + Vector3.up * (q.y - .035f));
    }
    void Fit(District area, Transform parent, Func<Vector3, Vector3> map)
    {
        doors = area.doors;
        boards = new GameObject("House doors and signboards");
        boards.transform.SetParent(parent, true);
        var timber = new Plates();
        var lettering = new Plates();
        int rows = Mathf.NextPowerOfTwo(Mathf.CeilToInt(register.signs.Length / 4f));
        foreach (var d in doors)
        {
            var p = V(d.point);
            d.position = map(p);
            d.outward = (map(p + V(d.normal)) - d.position).normalized;
            if (d.millPassage)
            {
                Vector3 stone = d.position - d.outward * .035f;
                timber.Add(stone, d.outward, 2.25f, 2.18f, 3, 8, 4);
                timber.Add(stone + Vector3.up * 1.22f, d.outward, 2.52f, .32f, 16, 8, 4);
                timber.Add(stone + Vector3.up * 1.47f, d.outward, 2.26f, .22f, 3, 8, 4);
            }
            if (d.paintDoor)
                timber.Add(d.position, d.outward, 1.16f, 2.09f, 22, 8, 4);
            if (d.sign < 0)
                continue;
            var sign =
                d.position + d.outward * (d.openSpace ? .065f : .24f) + Vector3.up * (d.openSpace ? .54f : 1.56f);
            if (d.openSpace)
                timber.Add(sign - Vector3.up * .92f, d.outward, .18f, 1.9f, 1, 8, 4);
            lettering.Add(sign, d.outward, 1.86f, .81f, d.sign, 4, rows);
        }
        Attach(timber, "RoomPaint");
        Attach(lettering, "HouseSigns");
    }
    public void StallSign(Transform stall, string name)
    {
        int cell = Array.IndexOf(register.signs, name);
        if (cell < 0 || boards == null)
            return;
        var sign = new Plates();
        int rows = Mathf.NextPowerOfTwo(Mathf.CeilToInt(register.signs.Length / 4f));
        sign.Add(stall.TransformPoint(new Vector3(0, .52f, .54f)), stall.forward, 1.52f, .58f, cell, 4, rows);
        Attach(sign, "HouseSigns");
    }
    sealed class Plates
    {
        public readonly List<Vector3> points = new List<Vector3>();
        public readonly List<Vector2> uv = new List<Vector2>();
        public readonly List<int> tris = new List<int>();
        public void Add(Vector3 centre, Vector3 front, float w, float h, int cell, int cols, int rows)
        {
            Vector3 right = Vector3.Cross(front, Vector3.up) * w * .5f, up = Vector3.up * h * .5f;
            int i = points.Count;
            points.AddRange(
                new[] { centre - right - up, centre + right - up, centre - right + up, centre + right + up });
            foreach (var q in new[] { Vector2.zero, Vector2.right, Vector2.up, Vector2.one })
                uv.Add(new Vector2((cell % cols + .025f + .95f * q.x) / cols,
                                   1 - (cell / cols + .975f - .95f * q.y) / rows));
            tris.AddRange(new[] { i, i + 2, i + 1, i + 1, i + 2, i + 3 });
        }
    }
    void Attach(Plates plates, string file)
    {
        if (plates.points.Count == 0)
            return;
        var mesh = new Mesh();
        mesh.SetVertices(plates.points);
        mesh.SetUVs(0, plates.uv);
        mesh.SetTriangles(plates.tris, 0);
        var colors = new Color32[plates.points.Count];
        for (int i = 0; i < colors.Length; i++)
            colors[i] = new Color32(255, 255, 255, 255);
        mesh.colors32 = colors;
        mesh.RecalculateBounds();
        boardMeshes.Add(mesh);
        var m = Paint(file);
        boardMaterials.Add(m);
        var part = new GameObject(file);
        part.transform.SetParent(boards.transform, false);
        part.AddComponent<MeshFilter>().sharedMesh = mesh;
        part.AddComponent<MeshRenderer>().sharedMaterial = m;
    }
    void Show(string title, string body)
    {
        if (captionTitle != title || caption != body)
        {
            display.Say(title, body);
            captionTitle = title;
            caption = body;
        }
    }
    Address Target()
    {
        Address best = null;
        float score = -10;
        foreach (var d in doors)
        {
            var delta = d.position - player.head.position;
            float dist = delta.magnitude;
            if (dist > 3.25f || dist < .01f || Vector3.Dot(delta, d.outward) > .18f)
                continue;
            float dot = Vector3.Dot(delta / dist, player.head.forward);
            if (dot < .71f || dot - dist * .035f <= score)
                continue;
            if (Physics.Raycast(player.head.position, delta / dist, Mathf.Max(0, dist - .48f),
                                1 << MeadowWorld.GroundLayer, QueryTriggerInteraction.Ignore))
                continue;
            score = dot - dist * .035f;
            best = d;
        }
        return best;
    }
    bool Looking(Vector3 local)
    {
        var d = roomOrigin + local - player.head.position;
        return d.magnitude < 2.85f && Vector3.Dot(d.normalized, player.head.forward) > .55f;
    }
    public bool Tick(bool action, Transform storyTarget = null)
    {
        if (active != null)
        {
            if (reading)
            {
                Show(active.objectName, active.lore);
                if (action)
                    reading = false;
                return true;
            }
            bool exit = Looking(Local(0, 1.24f, 3.27f)), note = Looking(Local(0, 1.12f, -2.5f));
            if (exit || note)
                Show(active.name.Length > 0 ? active.name : "A private house",
                     exit ? "E / trigger · Go outside" : "E / trigger · Read the record");
            else if (caption != null)
            {
                display.Hide();
                caption = null;
            }
            if (exit && action)
                Leave();
            else if (note && action)
                reading = true;
            return true;
        }
        var d = Target();
        if (d == null)
        {
            if (caption != null)
            {
                display.Hide();
                caption = null;
            }
            notice = null;
            return false;
        }
        if (storyTarget != null)
        {
            var aim = storyTarget.position - player.head.position;
            float dot = Vector3.Dot(aim.normalized, player.head.forward);
            if (aim.magnitude < 4.1f && dot > .97f &&
                dot > Vector3.Dot((d.position - player.head.position).normalized, player.head.forward))
            {
                caption = null;
                return false;
            }
        }
        if (notice != d)
            notice = null;
        Show(notice != null ? d.name
             : d.openSpace  ? "Signboard"
                            : "Doorway",
             notice != null ? d.lore
             : d.openSpace  ? "E / trigger · Read sign"
                            : "E / trigger · Enter");
        if (action)
        {
            if (d.openSpace)
            {
                notice = notice == null ? d : null;
            }
            else
                Enter(d);
        }
        return true;
    }
    void Enter(Address d)
    {
        var asset = Resources.Load<TextAsset>(Path + d.layout);
        var data = JsonUtility.FromJson<Shell>(asset.text);
        int count = data.light.Length;
        var verts = new Vector3[count];
        var uv = new Vector2[count];
        var colors = new Color[count];
        for (int i = 0; i < count; i++)
        {
            verts[i] = Local(data.pos[3 * i], data.pos[3 * i + 1], data.pos[3 * i + 2]);
            uv[i] = new Vector2(data.uv[2 * i], data.uv[2 * i + 1]);
            float l = data.light[i];
            colors[i] = new Color(l, l, l, 1);
        }
        // Reflecting Z reverses the winding of the exported Blender faces.
        for (int i = 0; i < data.indices.Length; i += 3)
        {
            int second = data.indices[i + 1];
            data.indices[i + 1] = data.indices[i + 2];
            data.indices[i + 2] = second;
        }
        roomMesh = new Mesh { name = d.layout };
        roomMesh.vertices = verts;
        roomMesh.uv = uv;
        roomMesh.colors = colors;
        roomMesh.triangles = data.indices;
        roomMesh.RecalculateBounds();
        room = new GameObject(d.name.Length > 0 ? d.name : "House");
        room.transform.position = roomOrigin;
        room.layer = MeadowWorld.GroundLayer;
        roomMaterial = Paint("RoomPaint");
        room.AddComponent<MeshFilter>().sharedMesh = roomMesh;
        room.AddComponent<MeshRenderer>().sharedMaterial = roomMaterial;
        room.AddComponent<MeshCollider>().sharedMesh = roomMesh;
        active = d;
        returnFeet = player.head.position;
        returnFeet.y = player.transform.position.y;
        returnFacing = player.transform.rotation;
        caption = null;
        display.Hide();
        Physics.SyncTransforms();
        player.Teleport(roomOrigin + Local(0, .06f, 1.95f), Quaternion.identity);
    }
    void Leave()
    {
        if (room != null)
        {
            room.SetActive(false);
            Object.Destroy(room);
            Object.Destroy(roomMesh);
            Object.Destroy(roomMaterial);
        }
        active = null;
        reading = false;
        caption = null;
        display.Hide();
        if (player != null)
            player.Teleport(returnFeet, returnFacing);
    }
    public void ClearVillage(Transform village)
    {
        if (boards != null && boards.transform.parent == village)
            Clear();
    }
    public void Clear()
    {
        if (active != null)
            Leave();
        if (boards != null)
            Object.Destroy(boards);
        foreach (var m in boardMeshes)
            Object.Destroy(m);
        foreach (var m in boardMaterials)
            Object.Destroy(m);
        boardMeshes.Clear();
        boardMaterials.Clear();
        doors = Array.Empty<Address>();
        notice = null;
        caption = null;
    }
}
}
