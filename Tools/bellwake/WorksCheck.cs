// Compile with BellwakeWorks.cs and System.Web.Extensions, then pass the authored JSON plan.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Web.Script.Serialization;
using Wizzard;

class WorksCheck
{
    static void Require(bool condition, string message)
    {
        if (!condition)
            throw new Exception(message);
    }
    static void Run(BellwakeWorks w, string stations)
    {
        foreach (var id in stations.Split(' '))
        {
            string to;
            Require(w.Station("A_" + id) != null, w.Room.key + " has no station " + id);
            w.Use("A_" + id, out to);
        }
    }
    static BellwakeWorks Reload(WorksPlan plan, BellwakeWorks w)
    {
        var resume = new BellwakeWorks { active = w.active, chamber = w.chamber, camp = w.camp, badges = w.badges,
                                         machines = (int[])w.machines.Clone() };
        resume.Bind(plan);
        return resume;
    }
    static bool Target(WorksMachine m, WorksRow row)
    {
        Func<string, int> s = key => row.values[Array.IndexOf(m.channels, key)];
        if (m.channels[0].StartsWith(m.key)) return row.values[row.values.Length-1]==1;
        switch (m.key)
        {
        case "water":
            return s("deep") == 4;
        case "record":
            return s("verse") == 4;
        case "crane":
            return s("level") == 1;
        case "cast":
            return s("finished") == 1;
        case "prism":
            return s("moon") * s("sun") == 1;
        case "orbits":
            return s("oak") == 2 && s("wren") == 1 && s("tide") == 2;
        case "lampcode":
            return s("signalBar") == 3;
        default:
            return s("phrase") == 5;
        }
    }
    static void Main(string[] args)
    {
        var plan = new JavaScriptSerializer().Deserialize<WorksPlan>(File.ReadAllText(args[0]));
        int positions = 0, actions = 0;
        foreach (var m in plan.machines)
        {
            var reverse = m.rows
                              .Select(
                                  _ => new List<int>())
                              .ToArray();
            var q = new Queue<int>();
            var good = new HashSet<int>();
            for (int i = 0; i < m.rows.Length; i++)
            {
                var r = m.rows[i];
                positions++;
                actions += r.moves.Length;
                Require(r.moves.Length == m.controls.Length && r.values.Length == m.channels.Length,
                        m.key + " schema");
                foreach (int to in r.moves)
                    reverse[to].Add(i);
                if (Target(m, r))
                {
                    good.Add(i);
                    q.Enqueue(i);
                }
            }
            while (q.Count > 0)
                foreach (int i in reverse[q.Dequeue()])
                    if (good.Add(i))
                        q.Enqueue(i);
            Require(good.Count == m.rows.Length, m.key + " stranded mechanism");
        }
        var pilgrimage = new BellwakeWorks { active=true, chamber=Array.FindIndex(plan.rooms,r=>r.early) };
        pilgrimage.Bind(plan);
        Require(pilgrimage.GuideTrail(0).Count == 0, "unearned waywren");
        foreach (var room in plan.rooms.Where(r=>r.early))
        {
            Require(pilgrimage.Room == room, "cross-ward journey");
            string destination;
            pilgrimage.Use("A_Gate",out destination);
            Require(string.IsNullOrEmpty(destination), "unearned road wicket");
            foreach (var station in room.stations.Where(s=>!string.IsNullOrEmpty(s.trail) && s.id!="A_Gate"))
            {
                pilgrimage.Use(station.id,out destination);
                pilgrimage = Reload(plan,pilgrimage);
                Require(pilgrimage.camp==station.camp && pilgrimage.Signal(room.key+station.id.Substring(2))==1, "lost ward shelter");
                for (int cell=0;cell<225;cell++)
                {
                    var track=pilgrimage.GuideTrail(cell);
                    Require(track.Count>=1 && track.Count<=5 && track[0]==cell, "lost guide");
                    for (int i=1;i<track.Count;i++)
                        Require(Math.Abs(track[i]%15-track[i-1]%15)+Math.Abs(track[i]/15-track[i-1]/15)==1, "guide jumped junction");
                }
            }
            pilgrimage.Use("A_Bell",out destination);
            Require(destination=="#RestTalk" && pilgrimage.camp=="RestTalk", "return line");
            pilgrimage.Use("A_Fast",out destination);
            Require(destination=="#RestGate" && pilgrimage.camp=="RestGate", "mile line");
            pilgrimage.Use("A_Gate",out destination);
            Require(!string.IsNullOrEmpty(destination) && pilgrimage.camp=="", "gate checkpoint");
            if(room.key=="RainCourt") Require(destination=="@choir","missing choir connection");
        }
        foreach (string order in new[] { "012", "021", "102", "120", "201", "210" })
        {
            var w = new BellwakeWorks { active = true };
            w.Bind(plan);
            Run(w, "Heart Intake");
            Require(w.chamber == 0, "unearned admission");
            Run(w, "Nema Roll");
            foreach (char wing in order)
            {
                if (wing == '0')
                {
                    Run(w, "Intake Fen Spring West DrainA West Spring West");
                    w = Reload(plan, w);
                    Require(w.Signal("deep") == 4, "lost tank level");
                    Run(w, "Float Archive Orrel Roof Oar Mill Reed Take Home Home");
                }
                else if (wing == '1')
                {
                    Run(w, "Crane Brannic One Two Four Four Brake Kiln Sand Wax Pour Vent Cool Take Home Home");
                }
                else
                {
                    Run(w, "Court Left Left Catch Fork Right Right Right Catch Iris Loft Oak Oak Wren Wren " +
                           "Wren Tide Tide Tide Take Short");
                }
                Require(w.chamber == 0, "return lift");
            }
            Run(w, "Crane Kiln Ossa Home Home Nema Heart");
            string dest;
            w.Use("A_Final", out dest);
            Require(String.IsNullOrEmpty(dest), "premature finale");
            Run(w, "River Forge Sky River Forge Sky River Sky Listen");
            w = Reload(plan, w);
            w.Use("A_Final", out dest);
            Require(dest == "Wrenfall", "missing coastal approach");
            Run(w, "Wing Depth Book");
            Require(w.Signal("signalBar") == 0 && w.Signal("sounding") == 0, "unearned passage");
            Run(w, "Pilot Transit Depth Lookout Bell Wing");
            w = Reload(plan,w);
            Require(w.Signal("signalBar") == 1, "coast checkpoint");
            Run(w,"Bell Star Launch");
            w.Use("A_Book",out dest);
            Require(dest == "@final" && w.Signal("named") == 1 && w.Signal("answered") == 1, "lost resolution");
        }
        Console.WriteLine(positions + " machine positions, " + actions +
                          " transitions, six wing orders, optional register and finale passed.");
    }
}
