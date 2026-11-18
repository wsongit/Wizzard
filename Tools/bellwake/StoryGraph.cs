// Compile this with Assets/Scripts/BellwakeJourney.cs. The offline edition reads
// the resulting transition table so both editions use the same puzzle rules.
using System;
using System.Collections.Generic;
using System.IO;
using System.Web.Script.Serialization;
using Wizzard;

class StoryGraph
{
    static readonly List<BellwakeJourney> queue = new List<BellwakeJourney>();
    static readonly Dictionary<string, int> visited = new Dictionary<string, int>();
    static readonly JavaScriptSerializer json = new JavaScriptSerializer { MaxJsonLength = 16000000 };
    static int Intern(BellwakeJourney state)
    {
        string key = String.Join(",", state.room, state.seals, state.melody, state.water, state.lenses,
                                 state.wounds, state.strikes, state.ending, state.commissioned, state.challenged);
        if (!state.Valid())
            throw new Exception("Invalid reachable state " + key);
        int i;
        if (visited.TryGetValue(key, out i))
            return i;
        i = queue.Count;
        queue.Add(state);
        visited[key] = i;
        return i;
    }
    static BellwakeJourney Copy(BellwakeJourney state)
    {
        return new BellwakeJourney { room = state.room,
                                     seals = state.seals,
                                     melody = state.melody,
                                     water = state.water,
                                     lenses = state.lenses,
                                     wounds = state.wounds,
                                     strikes = state.strikes,
                                     ending = state.ending,
                                     commissioned = state.commissioned,
                                     challenged = state.challenged };
    }
    static void Main(string[] args)
    {
        Intern(new BellwakeJourney());
        var rows = new List<object>();
        var reverse = new List<int[]>();
        var ends = new List<int>();
        for (int index = 0; index < queue.Count; index++)
        {
            var s = queue[index];
            var moves = new Dictionary<string, object>();
            var targets = new List<int>();
            var ids = new List<string> { "A_Talk", "A_Letter", "A_Gate" };
            if (s.ending > 0)
                ids.Add(s.ending == 1 ? "A_Roster" : "A_Ina");
            if (s.room > 0)
                ids.AddRange(new[] { "A_Key0", "A_Key1", "A_Key2" });
            if (s.room == 3)
                ids.Add("A_Lens");
            if (s.room == 4)
                ids.AddRange(new[] { "A_End0", "A_End1", "Toll" });
            foreach (var id in ids)
            {
                var t = Copy(s);
                string message;
                switch (id)
                {
                case "A_Ina":
                case "A_Roster":
                    message = t.Epilogue();
                    break;
                case "A_Talk":
                    message = t.Talk();
                    break;
                case "A_Letter":
                    message = t.ReadLetter();
                    t.letters = 0;
                    break;
                case "A_Gate":
                    message = t.Gate() ? "" : t.Objective();
                    break;
                case "A_Lens":
                    message = t.BeamCount == 4 ? "Molten amber sings in the casting cup."
                                               : "The casting cup is cold. Trace the light back to the kiln.";
                    break;
                case "A_End0":
                case "A_End1":
                    message = t.Choose(id == "A_End0" ? 1 : 2) ? "" : t.Objective();
                    break;
                case "Toll":
                    message = t.Miss();
                    break;
                default:
                    message = t.Key(id[id.Length - 1] - '0');
                    break;
                }
                int target = Intern(t);
                moves[id] = new object[] { target, message };
                targets.Add(target);
            }
            reverse.Add(targets.ToArray());
            if (s.ending != 0)
                ends.Add(index);
            rows.Add(new { room = s.room, seals = s.seals, melody = s.melody, water = s.water, lenses = s.lenses,
                           strikes = s.strikes, hearts = 3 - s.wounds, ending = s.ending,
                           commissioned = s.commissioned, challenged = s.challenged, solved = s.Solved,
                           called = s.CalledKey, beam = s.BeamCount, objective = s.Objective(),
                           keys = s.room == 0 ? new string[0] : new[] { s.KeyName(0), s.KeyName(1), s.KeyName(2) },
                           moves = moves });
        }
        foreach (int ending in new[] { 1, 2 })
        {
            var good = new HashSet<int>();
            foreach (var i in ends)
                if (queue[i].ending == ending)
                    good.Add(i);
            bool change;
            do
            {
                change = false;
                for (int i = 0; i < reverse.Count; i++)
                    foreach (int j in reverse[i])
                        if (good.Contains(j) && good.Add(i))
                        {
                            change = true;
                            break;
                        }
            } while (change);
            for (int i = 0; i < queue.Count; i++)
                if (queue[i].ending == 0 && !good.Contains(i))
                    throw new Exception("Soft lock at " + i);
        }
        File.WriteAllText(
            args[0], json.Serialize(new { states = rows, rooms = BellwakeJourney.Rooms,
                                          titles = BellwakeJourney.Titles, speakers = BellwakeJourney.Speakers }));
        Console.WriteLine(queue.Count +
                          (" reachable states. Both endings reachable from every unfinished " + "state."));
    }
}
