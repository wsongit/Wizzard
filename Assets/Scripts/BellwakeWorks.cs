using System;
using System.Collections.Generic;

namespace Wizzard
{
    [Serializable]
    public sealed class WorksPlan
    {
        public string[] flags;
        public WorksMachine[] machines;
        public WorksRoom[] rooms;
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
        public string key, title, intro, theme;
        public WorksStation[] stations;
        public WorksVisual[] visuals;
    }
    [Serializable]
    public sealed class WorksStation
    {
        public string id, label;
        public int note;
        public WorksRule[] rules;
    }
    [Serializable]
    public sealed class WorksRule
    {
        public string line, award, move, to;
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
        public string node, signal, kind;
        public float amount;
        public int match;
    }

    [Serializable]
    public sealed class BellwakeWorks
    {
        public bool active;
        public int chamber, badges;
        public int[] machines;
        [NonSerialized]
        WorksPlan plan;
        [NonSerialized]
        Dictionary<string, int> signals;
        public WorksRoom Room => plan.rooms[chamber];
        public void Bind(WorksPlan layout)
        {
            plan = layout;
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
                signals[plan.flags[i]] = (badges >> i) & 1;
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
            return index >= 0 && (badges & (1 << index)) != 0;
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
        public string Objective()
        {
            if (chamber != 0)
                return Room.intro;
            if (Signal("admitted") == 0)
                return Room.intro;
            if (Signal("reed") * Signal("yoke") * Signal("glass") != 0)
                return "All three witnesses are present. Take the northeastern resonator lift.";
            return "Find the trades' witnesses. River reed " + Signal("reed") + "/1, bronze yoke " +
                   Signal("yoke") + "/1, nightglass " + Signal("glass") + "/1.";
        }
        public WorksStation Station(string id)
        {
            return Array.Find(Room.stations, s => s.id == id);
        }
        public string Use(string id, out string destination)
        {
            destination = "";
            var station = Station(id);
            if (station == null)
                return Objective();
            foreach (var rule in station.rules)
            {
                if (Array.Exists(rule.when, c => Signal(c.signal) != c.value))
                    continue;
                if (!string.IsNullOrEmpty(rule.award))
                    badges |= 1 << Array.IndexOf(plan.flags, rule.award);
                if (!string.IsNullOrEmpty(rule.move))
                {
                    string[] command = rule.move.Split('.');
                    int i = Array.FindIndex(plan.machines, candidate => candidate.key == command[0]);
                    var m = plan.machines[i];
                    machines[i] = m.rows[machines[i]].moves[Array.IndexOf(m.controls, command[1])];
                }
                Refresh();
                destination = rule.to;
                if (!string.IsNullOrEmpty(destination) && destination != "@final")
                    chamber = Array.FindIndex(plan.rooms, r => r.key == rule.to);
                string line = rule.line;
                if (line.Contains("{"))
                    foreach (var value in signals)
                        line = line.Replace("{" + value.Key + "}", value.Value.ToString());
                return line;
            }
            return Objective();
        }
    }
}
