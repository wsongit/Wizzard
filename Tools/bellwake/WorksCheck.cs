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
        case "paperstage": return s("paperCredit")!=0;
        case "potcall": return s("supperBeat")==9;
        case "distribution": return s("drumBearing")==2;
        case "towlines": return s("towJob")==4;
        case "moulds": return s("craneJob")==3;
        case "weaving": return s("loomFlag")==4;
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
    static BellwakeWorks SolveGallery(WorksPlan plan, BellwakeWorks w, string key)
    {
        int index=Array.FindIndex(plan.machines,candidate=>candidate.key==key);
        var m=plan.machines[index];
        var queue=new Queue<int>();
        var routes=new Dictionary<int,List<int>>();
        int current=w.machines[index];
        queue.Enqueue(current);
        routes[current]=new List<int>();
        while(queue.Count>0)
        {
            current=queue.Dequeue();
            if(Target(m,m.rows[current])) break;
            for(int a=0;a<m.controls.Length;a++)
            {
                int next=m.rows[current].moves[a];
                if(routes.ContainsKey(next))continue;
                routes[next]=new List<int>(routes[current]) { a };
                queue.Enqueue(next);
            }
        }
        Require(Target(m,m.rows[current]),"disconnected gallery");
        int actions=0;
        foreach(int input in routes[current])
        {
            string op=m.controls[input], station=char.ToUpper(op[0])+op.Substring(1), dest;
            var s=w.Station("A_"+station);
            Require(s!=null, "missing "+station);
            int expected=m.rows[w.machines[index]].moves[input];
            w.Use(s.id,out dest);
            Require(w.machines[index]==expected,"incorrect physical command "+s.id);
            if (++actions%7==0) {w=Reload(plan,w);Require(w.camp==s.camp,"lost machine shelter");}
        }
        Require(Target(m,m.rows[w.machines[index]]),"unfinished dock work");
        return w;
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
        foreach (string credit in new[] {"Maker","Runner"})
        {
            var court=new BellwakeWorks {active=true,chamber=Array.FindIndex(plan.rooms,r=>r.prologue)};
            court.Bind(plan);
            Run(court,"Maker Light");
            Require(court.Signal("paperCredit")==0 && court.Signal("paperAct")==0,"unearned programme");
            string[] objects={"Pattern","Log","Boot","Carbon"};
            int[,] cues={{0,0,2},{2,2,1},{1,1,0},{1,0,2}};
            string[] reels={"Figure","Place","Prop"}, channels={"paperActor","paperPlace","paperProp"};
            for(int act=0;act<4;act++)
            {
                for(int j=0;j<3;j++) while(court.Signal(channels[j])!=cues[act,j]) Run(court,reels[j]);
                Run(court,"Light");
                Require(court.Signal("paperAct")==act,"skipped keepsake");
                Run(court,objects[act]+" Light");
                court=Reload(plan,court);
                Require(court.Signal("paperPlayed"+act)==1,"missing act");
            }
            Run(court,credit+" Maker Runner");
            Require(court.Signal("paperCredit")==(credit=="Maker"?1:2),"overwritten credit");
            string destination;
            court.Use("A_Door",out destination);
            Require(destination=="@market","missing exit");
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
            Require(dest == "DrumHouse" && w.Signal("named") == 1 && w.Signal("answered") == 1, "lost coast connection");
            Run(w,"Final Loom");
            Require(w.Room.key=="DrumHouse","unearned passage");
            Run(w,"Kitchen Low High Low Middle Middle High High Low Middle Serve");
            Require(w.Signal("supperServed")==0 && w.KitchenJournal().Length==0,"unearned supper");
            Run(w,"Home");
            foreach(char c in order)
            {
                int desired=c-'0';
                while(w.Signal("drumBearing")!=desired) Run(w,"Turn");
                string[] doors={"Dock","Crane","Loom"}, machines={"towlines","moulds","weaving"};
                Run(w,doors[desired]);
                Run(w,"MessNote");
                var slip=plan.supperNotes[desired];
                Require(w.Station("A_MessNote").tune.Length==3 && Reload(plan,w).KitchenJournal().Contains(slip.notes),"lost tune");
                w=SolveGallery(plan,w,machines[desired]);
                Run(w,"Home");
                Require(w.Room.key=="DrumHouse","missing return");
            }
            Run(w,"Kitchen Serve");
            Require(Reload(plan,w).Signal("supperServed")==1,"missing kitchen visitors");
            Run(w,"Home");
            w.Use("A_Final",out dest);
            Require(dest=="@final","keeper ascent");
        }
        Console.WriteLine(positions + " machine positions, " + actions +
                          " transitions, six guild and Countertide gallery orders, machine checkpoints, optional register and finale passed.");
    }
}
