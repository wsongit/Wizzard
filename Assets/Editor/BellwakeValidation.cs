using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Wizzard.Editor
{
    public static class BellwakeValidation
    {
        [MenuItem("Wizzard/Validate Bellwake rooms")]
        public static void Validate()
        {
            var atlas=JsonUtility.FromJson<PassageAtlas>(Resources.Load<TextAsset>("Bellwake/Passages").text);
            var rooms=new List<string>(BellwakeJourney.Rooms);
            foreach(var region in atlas.regions) rooms.Add(region.key);
            var works=JsonUtility.FromJson<WorksPlan>(Resources.Load<TextAsset>("Bellwake/Underworks").text);
            foreach(var chamber in works.rooms) rooms.Add(chamber.key);
            foreach (string room in rooms)
            {
                string prefix = "Bellwake/";
                var scene = Resources.Load<GameObject>(prefix + "Rooms/" + room);
                Require(scene != null, "Missing room " + room);
                var names = new HashSet<string>();
                foreach (var t in scene.GetComponentsInChildren<Transform>(true))
                {
                    names.Add(t.name);
                    var mesh = t.GetComponent<MeshFilter>();
                    if (mesh == null)
                        continue;
                    Require(mesh.sharedMesh != null && mesh.sharedMesh.isReadable, room + " mesh " + t.name);
                    Require(mesh.sharedMesh.uv.Length == mesh.sharedMesh.vertexCount, room + " UVs " + t.name);
                    foreach (var m in t.GetComponent<MeshRenderer>().sharedMaterials)
                        Require(m != null && Resources.Load<Texture2D>(prefix + "Textures/" + m.name) != null,
                                room + " paint on " + t.name);
                }
                foreach (var marker in new[] { "Terrain", "Set", "C_Solids", "Spawn", "Look", "Rim" })
                    Require(names.Contains(marker), room + " marker " + marker);
                var chamber=Array.Find(works.rooms,r=>r.key==room);
                if(chamber!=null)
                {
                    foreach(var station in chamber.stations) Require(names.Contains(station.id),room+" "+station.id);
                    foreach(var visual in chamber.visuals) Require(names.Contains(visual.node),room+" "+visual.node);
                }
                else foreach(var id in new[]{"A_Talk","A_Gate","GateLight"}) Require(names.Contains(id),room+" "+id);
                if(chamber==null && Array.IndexOf(BellwakeJourney.Rooms,room)<0)
                {
                    foreach(var id in new[]{"Chart","Pawn","Cargo","NW","NE","SW","A_Key0","A_Key1","A_Key2","A_Key3","A_Stamp","A_Hint","A_Reset","A_Log0","A_Log1","A_Log2"})
                        Require(names.Contains(id),room+" marker "+id);
                    Require(Resources.Load<TextAsset>(prefix+"Charts/"+room)!=null,room+" charts");
                }
                else if(chamber==null) Require(names.Contains("A_Letter"),room+" letter");
                if (Array.IndexOf(BellwakeJourney.Rooms,room)>0)
                    for (int i = 0; i < 3; i++)
                        Require(names.Contains("A_Key" + i) && names.Contains("Rotor" + i),
                                room + " station " + i);
                string theme=chamber==null?room:chamber.theme;
                Require(Resources.Load<Cubemap>(prefix + "Skies/" + theme) != null, room + " sky");
                var clip = Resources.Load<AudioClip>(prefix + "Audio/" + theme);
                Require(clip != null && clip.length > 12, room + " music");
            }
            foreach (var file in new[] { "LeftPalm", "RightPalm", "RunnerArm", "TrailSign", "MeadowOutcrop",
                                         "MossbellApproach" })
                Require(Resources.Load<GameObject>("Bellwake/Rooms/" + file) != null, file);
            Require(Shader.Find("Wizzard/BellwakePaint") != null && Shader.Find("Wizzard/BellwakeSky") != null,
                    "Bellwake shaders");
            Debug.Log("Bellwake import checks passed for all campaign districts.");
        }
        static void Require(bool yes, string what)
        {
            if (!yes)
                throw new InvalidOperationException("Invalid Bellwake asset: " + what);
        }
    }
}
