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
                    if (BellwakeCampaign.IsCollisionSurface(t.name))
                    {
                        var surfaces=t.GetComponents<MeshCollider>();
                        Require(surfaces.Length==1 && surfaces[0].sharedMesh==mesh.sharedMesh &&
                                t.gameObject.layer==MeadowWorld.GroundLayer,room+" collision mesh "+t.name);
                    }
                    Require(mesh.sharedMesh != null && mesh.sharedMesh.isReadable, room + " mesh " + t.name);
                    Require(mesh.sharedMesh.uv.Length == mesh.sharedMesh.vertexCount, room + " UVs " + t.name);
                    foreach (var m in t.GetComponent<MeshRenderer>().sharedMaterials)
                        Require(m != null && Resources.Load<Texture2D>(prefix + "Textures/" + m.name) != null,
                                room + " paint on " + t.name);
                }
                foreach (var marker in new[] { "Terrain", "Set", "C_Solids", "Spawn", "Look", "Rim" })
                    Require(names.Contains(marker), room + " marker " + marker);
                foreach (var name in names)
                    if (name.StartsWith("Hit_"))
                        Require(names.Contains("Edge_" + name.Substring(4)) && names.Contains("A_" + name.Substring(4)), room+" "+name);
                if (room=="Bellmarket" || room=="Reedwater") Require(names.Contains("A_Packet"),room+" packet counter");
                if (room=="Bellmarket")
                    Require(names.Contains("A_WoodWalk") && names.Contains("A_RoadBook") && names.Contains("RoadBook"), "market road letters");
                if (room=="StillBelfry")
                {
                    foreach (var part in new[]{"KeeperMask","KeeperLeft","KeeperRight","KeeperLamp","KeeperCue0","KeeperCue1","KeeperCue2","A_MorningSong"})
                        Require(names.Contains(part),room+" "+part);
                }
                var chamber=Array.Find(works.rooms,r=>r.key==room);
                if(chamber!=null)
                {
                    foreach(var station in chamber.stations) Require(names.Contains(station.id),room+" "+station.id);
                    foreach(var station in chamber.stations)
                        if (!string.IsNullOrEmpty(station.sight)) Require(names.Contains(station.sight),room+" "+station.sight);
                    foreach (var station in chamber.stations)
                    {
                        if (!string.IsNullOrEmpty(station.call))
                            Require(Resources.Load<AudioClip>(prefix+"Audio/"+station.call)!=null,room+" listening call "+station.call);
                        if (!string.IsNullOrEmpty(station.swing)) Require(names.Contains(station.swing), room+" "+station.swing);
                        if (!string.IsNullOrEmpty(station.tune)) Require(Array.TrueForAll(station.tune.ToCharArray(), n=>n>='0' && n<='2'), room+" bad tune");
                    }
                    foreach (var station in chamber.stations)
                        if (!string.IsNullOrEmpty(station.camp)) Require(names.Contains(station.camp),room+" "+station.camp);
                    if (chamber.early)
                    {
                        foreach (string part in new[] {"MapSW","MapSE","MapNW","GuideBird","GuideLeft","GuideRight"})
                            Require(names.Contains(part),room+" "+part);
                        Require(chamber.ground.Length==225, room+" guide heights");
                    }
                    foreach (var source in works.rooms)
                        foreach (var station in source.stations)
                            foreach (var rule in station.rules)
                                if (rule.to==room && !string.IsNullOrEmpty(rule.arrival))
                                    Require(names.Contains(rule.arrival), room+" arrival "+rule.arrival);
                    foreach(var visual in chamber.visuals)
                    {
                        Require(names.Contains(visual.node),room+" "+visual.node);
                        if (!string.IsNullOrEmpty(visual.mount)) Require(names.Contains(visual.mount),room+" "+visual.mount);
                        if (!string.IsNullOrEmpty(visual.visibleSignal)) Require(Array.IndexOf(works.flags,visual.visibleSignal)>=0,room+" missing visibility flag");
                        if (visual.kind=="slide") Require(names.Contains("RailStart") && names.Contains("RailEnd"),room+" slide guides");
                        if (visual.kind=="pointer")
                            foreach (var bearing in new[]{"Bearing0","Bearing1","Bearing2"}) Require(names.Contains(bearing),room+" selector index");
                        if (visual.kind=="voyage") Require(names.Contains(visual.node+"Turn") && names.Contains(visual.node+"Berth"),room+" vessel route");
                    }
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
            foreach (string print in new[]{"ContactSheet","Tavi","RowanLinen"})
                Require(Resources.Load<Texture2D>("Bellwake/Letters/"+print)!=null,"Missing book illustration "+print);
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
