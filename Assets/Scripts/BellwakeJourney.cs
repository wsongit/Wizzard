using System;

namespace Wizzard
{
    // This is the saved game and the rules used by the live interactions.
    [Serializable]
    public sealed class BellwakeJourney
    {
        public BellwakePassage passage;
        public BellwakeWorks works;
        public float[] secondsByPlace;
        public string PlayTime()
        {
            double seconds=0;
            if (secondsByPlace!=null) foreach (float t in secondsByPlace) seconds+=t;
            var time=TimeSpan.FromSeconds(seconds);
            return ((int)time.TotalHours)+"h "+time.Minutes+"m";
        }
        public int version = 1;
        public int room, seals, melody, water, lenses = 4, wounds, strikes, letters, ending;
        public bool commissioned, challenged;
        public static readonly string[] Rooms = { "Bellmarket", "RootChoir", "Reedwater", "CinderLens",
                                                  "StillBelfry" };
        public static readonly string[] Titles = { "Bellmender's Market", "The Root Choir", "Reedwater Lock",
                                                   "The Cinder Lens", "The Still Belfry" };
        public static readonly string[] Speakers = { "Tavi", "Moss", "Fen", "Ossa", "The Quiet" };
        static readonly string[][] Keys = { new string[0], new[] { "Wren", "Root", "Rain" },
                                            new[] { "Mill + fen", "Fen + quarry", "Quarry" },
                                            new[] { "West lens", "North lens", "East lens" },
                                            new[] { "Leaf", "Ember", "Tide" } };
        static readonly int[] Song = { 2, 1, 0 };
        static readonly int[] Valves = { 3, 6, 4 };
        static readonly int[] CounterSong = { 0, 2, 1 };
        static readonly string[] Pages = {
            "A child's drawing of a bell. There are two figures underneath. One has been rubbed away.",
            "Moss kept the ribbon from Ina's coat. Inside the hem she stitched three things that make a sound " +
            "after " +
                "rain.",
            "A page from the lock book. In the flood, Ina opened the mill channel by hand. Every family " +
            "downstream " +
                "lived.",
            "A casting receipt in Tavi's hand. One bronze bell. Payment: one voice, freely given. Duration: " +
            "until " +
                "morning.",
            "Ina scratched a line into the yoke: If I forget my name, please tell me what the river sounds like."
        };
        public int NextRoom
        {
            get {
                return Math.Min(4, seals + 1);
            }
        }
        public bool Solved
        {
            get {
                return room > 0 && (room <= seals || (room == 4 && strikes == 3));
            }
        }
        public bool Valid()
        {
            return version == 1 && room >= 0 && room <= 4 && seals >= 0 && seals <= 3 && room <= NextRoom &&
                   melody >= 0 && (melody < 3 || (melody == 3 && seals >= 1)) && water >= 0 && water < 8 &&
                   lenses >= 0 && lenses < 8 && wounds >= 0 && wounds <= 2 && strikes >= 0 && strikes <= 3 &&
                   letters >= 0 && letters < 32 && ending >= 0 && ending <= 2 &&
                   (commissioned || (room == 0 && seals == 0 && ending == 0)) &&
                   (ending == 0 || (room == 0 && strikes == 3 && seals == 3));
        }
        public string KeyName(int key)
        {
            return Keys[room][key];
        }
        public int CalledKey
        {
            get {
                return CounterSong[Math.Min(2, strikes)];
            }
        }
        public int BeamCount
        {
            get {
                return (lenses & 1) == 0 ? 1 : (lenses & 2) == 0 ? 2 : (lenses & 4) != 0 ? 3 : 4;
            }
        }
        public string Objective()
        {
            if (ending == 1)
                return "Epilogue  /  Hear Tavi's last letter.";
            if (ending == 2)
                return "Epilogue  /  Visit Tavi in the morning market.";
            if (room == 0)
                return commissioned ? "Follow the brass arch to " + Titles[NextRoom] + "."
                                    : "Find Tavi by the market path.";
            if (Solved)
                return room == 4 ? "Choose the bell's future at the two standards."
                                 : "The arch is awake. Follow its light.";
            switch (room)
            {
            case 1:
                return "Play the forest round on the three hanging bells.";
            case 2:
                return "Send water to the MILL alone.";
            case 3:
                return "Turn the three lenses until the light reaches the cup.";
            default:
                return challenged
                           ? "Answer the " + KeyName(CalledKey).ToUpperInvariant() + " seal before the toll."
                           : "Face the keeper under the great bell.";
            }
        }
        public string Talk()
        {
            if (room == 0)
            {
                if (ending == 1)
                    return "TAVI  /  I take the first watch tonight. Tomorrow it's the baker. Ina can finally " +
                           "sleep. Will you stay for bread?";
                if (ending == 2)
                    return "TAVI  /  I heard a girl laughing down by the lock. For the first time in twelve " +
                           "years " +
                           "the bell was perfectly still.";
                if (!commissioned)
                {
                    commissioned = true;
                    return "TAVI  /  The warning bell took my sister's voice. Now it's taking ours. Bring me " +
                           "the " +
                           "forest song, the river's course and the light that cast it.";
                }
                return "TAVI  /  My sister was called Ina. If the keeper asks what she was, tell it she was a " +
                       "person.";
            }
            if (room == 1)
                return "MOSS  /  First the RAIN drinks. Then the ROOT wakes. Last the WREN sings. Three bells, " +
                       "one " +
                       "breath. My gran sang it when Ina went to the lock.";
            if (room == 2)
                return "FEN  /  Ina opened the MILL to save us. Each wheel changes the channels on its plate. " +
                       "Leave " +
                       "the mill flowing and the FEN and QUARRY dry.";
            if (room == 3)
                return "OSSA  /  Follow that amber line from the kiln. Turn each mirror so it sends the ray to " +
                       "the " +
                       "next. I cast that bell to hold one night. Tavi never let it end.";
            if (strikes == 3)
                return "INA  /  I remember my name. Give the watch to everyone, or loose my voice into the " +
                       "river. " +
                       "Either way, I want to see morning.";
            challenged = true;
            return "THE QUIET  /  If I stop ringing, who will wake them? Answer the three seals before each " +
                   "toll. " +
                   "Follow my raised wing. Both wings call the seal behind me. Give me a voice I can send home.";
        }
        public string Epilogue()
        {
            return ending == 1
                       ? "WATCH ROSTER  /  Dusk: Tavi at the wheel. Midnight: Fen on the bridge. Dawn: Ossa at " +
                         "the " +
                             "bell. Underneath, in smaller letters: Let Ina sleep."
                       : "INA  /  I used to think a river made one sound. Stand a while. There's the water " +
                         "against " +
                             "the bank, the wheel turning, a wren in the reeds. I'm going to learn them all.";
        }
        public static string Leaf(int index)
        {
            return Pages[index];
        }
        public string ReadLetter()
        {
            letters |= 1 << room;
            return "WITNESS LEAF  /  " + Pages[room];
        }
        public string Key(int i)
        {
            if (room < 1 || i < 0 || i > 2 || Solved)
                return Objective();
            if (room == 1)
            {
                melody = i == Song[melody] ? melody + 1 : (i == Song[0] ? 1 : 0);
                if (melody == 3)
                {
                    seals = 1;
                    return "The canopy answers in three voices. You carry the forest round.";
                }
                return melody == 0 ? "The phrase falls quiet. Listen to Moss for the order."
                                   : KeyName(i) + " rings true. " + melody + " of three voices.";
            }
            if (room == 2)
            {
                water ^= Valves[i];
                if (water == 1)
                {
                    seals = 2;
                    return "The mill wheel catches. A child's voice rises through the culvert.";
                }
                return "MILL " + On(1) + "    FEN " + On(2) + "    QUARRY " + On(4);
            }
            if (room == 3)
            {
                lenses ^= 1 << i;
                if (BeamCount == 4)
                {
                    seals = 3;
                    return "The cup fills with furnace light. Ina's final note is waiting in the belfry.";
                }
                return "The beam reaches " + BeamCount + " of four conduits.";
            }
            if (!challenged)
                return "Speak to the keeper beneath the bell.";
            if (i != CalledKey)
                return Miss();
            strikes++;
            wounds = 0;
            return strikes == 3
                       ? "INA  /  I can hear you. I thought the whole world had gone quiet. Wind my little music box if you want to hear our kitchen song."
                       : "The bronze cracks. Answer the " + KeyName(CalledKey).ToUpperInvariant() + " seal.";
        }
        string On(int bit)
        {
            return (water & bit) != 0 ? "open" : "shut";
        }
        public string Miss()
        {
            if (room != 4 || !challenged || strikes == 3)
                return Objective();
            if (++wounds == 3)
            {
                wounds = 0;
                strikes = 0;
                challenged = false;
                return "The bell takes your breath. The keeper lowers its head. Speak to try again.";
            }
            return "A hollow toll. " + (3 - wounds) + " breaths remain. Find " + KeyName(CalledKey) + ".";
        }
        public bool Gate()
        {
            if (ending != 0 || !commissioned || room == 4 || (room != 0 && !Solved))
                return false;
            room = NextRoom;
            return true;
        }
        public bool Choose(int choice)
        {
            if (room != 4 || strikes != 3 || (choice != 1 && choice != 2))
                return false;
            ending = choice;
            room = 0;
            return true;
        }
        public int LeafCount
        {
            get {
                int n = 0;
                for (int i = 0; i < 5; i++)
                    if ((letters & (1 << i)) != 0)
                        n++;
                return n;
            }
        }
    }
}
