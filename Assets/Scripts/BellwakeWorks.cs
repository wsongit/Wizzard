using System;
using System.Collections.Generic;

namespace Wizzard
{
    [Serializable]
    public sealed class WorksPlan
    {
        public string logTitle, logEntry, theatreInvitation, pilotMail;
        public string[] logEndings, supperEndings, pilotEndings, swallowEntries, parishEndings, theatreCredits, theatreCadences;
        public SupperNote[] supperNotes;
        public RoadLeaf[] roadLeaves;
        public string parishLedger;
        public string[] flags;
        public WorksMachine[] machines;
        public WorksRoom[] rooms;
    }
    [Serializable]
    public sealed class SupperNote
    {
        public string signal, title, notes;
    }
    [Serializable]
    public sealed class RoadLeaf
    {
        public string name, shared, freed;
    }
    [Serializable]
    public sealed class WorksMachine
    {
        public string key;
        public string[] channels, controls;
        public WorksRow[] rows;
    }
    [Serializable]
    public sealed class WorksRow
    {
        public int[] values, moves;
    }
    [Serializable]
    public sealed class WorksRoom
    {
        public string key, title, intro, theme, score, chapter, fog;
        public bool early, prologue, middle;
        public WorksRule[] goals;
        public float halfSpan;
        public float[] ground;
        public WorksStation[] stations;
        public WorksVisual[] visuals;
    }
    [Serializable]
    public sealed class WorksStation
    {
        public string id, label, sight, search, evidence, direction, camp, trail, tune, swing, prime;
        public int note;
        public WorksRule[] rules;
    }
    [Serializable]
    public sealed class WorksRule
    {
        public string line, award, move, to, lead, arrival;
        public WorksCondition[] when;
    }
    [Serializable]
    public sealed class WorksCondition
    {
        public string signal;
        public int value;
    }
    [Serializable]
    public sealed class WorksVisual
    {
        public string node, signal, kind, stack, visibleSignal;
        public float amount, rise;
        public int match;
    }

    [Serializable]
    public sealed class BellwakeWorks
    {
        public bool active, invited, returnTicket;
        // The first 30 flags retain their original save positions in badges.
        const int FlagsPerWord = 30;
        public int chamber, badges;
        public int[] furtherBadges;
        public string camp;
        public int[] machines;
        [NonSerialized]
        WorksPlan plan;
        [NonSerialized]
        Dictionary<string, int> signals;
        public WorksRoom Room => plan.rooms[chamber];
        public void Bind(WorksPlan layout)
        {
            plan = layout;
            int words=Math.Max(0,(plan.flags.Length-1)/FlagsPerWord);
            if (furtherBadges==null || furtherBadges.Length!=words) Array.Resize(ref furtherBadges,words);
            if (machines == null || machines.Length != plan.machines.Length)
                Array.Resize(ref machines, plan.machines.Length);
            if (chamber < 0 || chamber >= plan.rooms.Length)
                chamber = 0;
            signals = new Dictionary<string, int>();
            for (int i = 0; i < machines.Length; i++)
                if (machines[i] < 0 || machines[i] >= plan.machines[i].rows.Length)
                    machines[i] = 0;
            Refresh();
        }
        void Refresh()
        {
            for (int i = 0; i < plan.flags.Length; i++)
                signals[plan.flags[i]] = HasBadge(i) ? 1 : 0;
            for (int i = 0; i < machines.Length; i++)
            {
                var m = plan.machines[i];
                var v = m.rows[machines[i]].values;
                for (int j = 0; j < v.Length; j++)
                    signals[m.channels[j]] = v[j];
            }
        }
        public int Signal(string name)
        {
            return signals[name];
        }
        public bool Remembered(WorksPlan layout, string name)
        {
            int index = Array.IndexOf(layout.flags, name);
            return index >= 0 && HasBadge(index);
        }
        bool HasBadge(int index)
        {
            int word = index / FlagsPerWord;
            int bits = word==0 ? badges : furtherBadges!=null && word<=furtherBadges.Length ? furtherBadges[word-1] : 0;
            return (bits & (1 << (index % FlagsPerWord))) != 0;
        }
        public string KitchenJournal()
        {
            var parts = new List<string>();
            foreach (var slip in plan.supperNotes)
                if (Signal(slip.signal) != 0) parts.Add(slip.title + "   ·   " + slip.notes);
            return string.Join("   /   ", parts);
        }
        public string Register()
        {
            if (Signal("named") != 0)
                return "Ina is on the night roll. Her nameplate will be waiting at the market.";
            if (Signal("token") != 0)
                return "Carry Ossa's nameplate back to Nema in the cistern.";
            if (Signal("petition") == 0)
                return "Nema keeps the night roll at the cistern entrance.";
            return "Fen’s knot " + Signal("knot") + "/1. Orrel’s pay leaf " + Signal("blank") +
                   "/1. Brannic’s spare wage " + Signal("wage") + "/1. Take the three proofs to Ossa.";
        }
        WorksRule NextGoal()
        {
            return Room.goals == null ? null : Array.Find(Room.goals, g =>
                Array.TrueForAll(g.when, c => Signal(c.signal) == c.value));
        }
        public List<int> GuideTrail(int cell)
        {
            var result = new List<int>();
            if (!Room.early || Signal("QuinceFoldKnife") == 0 || cell < 0 || cell >= 225) return result;
            var goal = NextGoal();
            var trail = goal == null ? null : Station(goal.lead)?.trail;
            if (string.IsNullOrEmpty(trail)) return result;
            result.Add(cell);
            for (int i = 0; i < 4 && trail[cell] != '.'; i++)
            {
                switch (trail[cell])
                {
                    case 'N': cell += 15; break;
                    case 'S': cell -= 15; break;
                    case 'E': cell++; break;
                    case 'W': cell--; break;
                    default: return result;
                }
                result.Add(cell);
            }
            return result;
        }
        public string Objective()
        {
            if (returnTicket && Room.key.StartsWith("Sillwater") && Signal("parishWarrant")==0)
                return "Welcome to Sillwater. Open your field sheet and find Ada near the south bell. The northeast towpath takes your return ticket whenever you want to leave.";
            if (returnTicket && Room.key.StartsWith("Sillwater") && Signal("parishSigned")!=0)
                return "Your signed title is in the witness book. Use your return ticket at the northeast towpath on either shore.";
            var goal = NextGoal();
            if (goal != null)
            {
                string objective=Format(goal.line);
                if (returnTicket && Room.key=="DriftFen") return objective+" Your return boat is at Swallow Stair.";
                if (returnTicket && Room.key=="SwallowLock") return objective+" The northeast towpath takes your return fare at any time.";
                return objective;
            }
            if (Room.key == "Wrenfall")
            {
                if (Signal("landed") != 0) return "The Linnet is at the north landing. Collect Elin’s flood book.";
                if (Signal("charter") == 0) return Room.intro;
                return "Field chart   /   Chapel: " + (Signal("sounding") != 0 ? "wing" : "unread") +
                    "   ·   Split Stone: " + (Signal("leading") != 0 ? "bell" : "unsighted") +
                    "   ·   Lookout: " + (Signal("distress") != 0 ? "star" : "unread") +
                    ". Eastern mast: " + Signal("signalBar") + " of 3 signals acknowledged.";
            }
            if (chamber != 0)
                return Room.intro;
            if (Signal("admitted") == 0)
                return Room.intro;
            if (Signal("reed") * Signal("yoke") * Signal("glass") != 0)
                return "All three witnesses are present. Take the northeastern resonator lift.";
            return "Find the trades' witnesses. River reed " + Signal("reed") + "/1, bronze yoke " +
                   Signal("yoke") + "/1, nightglass " + Signal("glass") + "/1.";
        }
        string Format(string line)
        {
            if (line.Contains("{"))
                foreach (var value in signals)
                    line=line.Replace("{"+value.Key+"}",value.Value.ToString());
            return line;
        }
        public WorksStation Station(string id)
        {
            return Array.Find(Room.stations, s => s.id == id);
        }
        public void TakePacket(bool fen = false)
        {
            active = true;
            returnTicket = true;
            chamber = Array.FindIndex(plan.rooms, r => r.key==(fen?"DriftFen":"SillwaterEbb"));
            camp = fen ? "RestGuide" : "RestGate";
        }
        public string Use(string id, out string destination)
        {
            destination = "";
            if (returnTicket && Room.middle && id == "A_Gate")
            {
                returnTicket = false;
                camp = "";
                destination = "@reedwater";
                return "";
            }
            var station = Station(id);
            if (station == null)
                return Objective();
            foreach (var rule in station.rules)
            {
                if (Array.Exists(rule.when, c => Signal(c.signal) != c.value))
                    continue;
                if (!string.IsNullOrEmpty(rule.award))
                {
                    int index=Array.IndexOf(plan.flags,rule.award);
                    int bit=1 << (index % FlagsPerWord);
                    if (index<FlagsPerWord) badges|=bit;
                    else furtherBadges[index/FlagsPerWord-1]|=bit;
                }
                if (!string.IsNullOrEmpty(rule.move))
                {
                    string[] command = rule.move.Split('.');
                    int i = Array.FindIndex(plan.machines, candidate => candidate.key == command[0]);
                    var m = plan.machines[i];
                    machines[i] = m.rows[machines[i]].moves[Array.IndexOf(m.controls, command[1])];
                }
                Refresh();
                destination = rule.to;
                if (!string.IsNullOrEmpty(station.camp)) camp = station.camp;
                if (!string.IsNullOrEmpty(destination))
                {
                    if (destination.StartsWith("#")) camp = destination.Substring(1);
                    else
                    {
                        camp = rule.arrival ?? "";
                        if (!destination.StartsWith("@")) chamber = Array.FindIndex(plan.rooms,r=>r.key==rule.to);
                    }
                }
                return Format(rule.line);
            }
            return Objective();
        }
    }
}
