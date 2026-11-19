using System;

namespace Wizzard
{
    // The booklet contains the legal moves and verified hints for just the current district.
    [Serializable]
    public sealed class PassageAtlas
    {
        public PassageRegion[] regions;
    }
    [Serializable]
    public sealed class PassageRegion
    {
        public string key, title, guide, thing, intro, rule, ending;
        public string[] sites, testimony, charts;
    }
    [Serializable]
    public sealed class PassageBook
    {
        public PassageBoard[] boards;
    }
    [Serializable]
    public sealed class PassageBoard
    {
        public string grid;
        public int goal, par;
        public PassagePosition[] states;
    }
    [Serializable]
    public sealed class PassagePosition
    {
        public int p, c, hint;
        public int[] move;
        public string[] paths;
        public bool win;
    }

    [Serializable]
    public sealed class BellwakePassage
    {
        public bool active;
        public int completed, sheet, position, logs;
        [NonSerialized]
        public PassageRegion region;
        [NonSerialized]
        public PassageBook book;
        [NonSerialized]
        public string travel;
        public static readonly string[] Bearings = { "North", "East", "South", "West" };
        public bool Done => sheet == region.charts.Length;
        public int Page => Math.Min(sheet, region.charts.Length - 1);
        public PassageBoard Board => book.boards[Page];
        public PassagePosition Piece => Board.states[position];
        public bool Surveyed => (logs & (1 << (Page / 3))) != 0;
        public void Bind(PassageRegion descriptor, PassageBook pages)
        {
            region = descriptor;
            book = pages;
            if (sheet < 0 || sheet > region.charts.Length)
                sheet = 0;
            if (position < 0 || position >= Board.states.Length)
                position = 0;
            logs &= 7;
        }
        public void Leave()
        {
            active = false;
            completed++;
            sheet = position = logs = 0;
            region = null;
            book = null;
        }
        public string Objective()
        {
            if (Done)
                return "The passage is open. Take the northern arch.";
            if (!Surveyed)
                return "Find the witness post at " + region.sites[Page / 3] + ".";
            if (Piece.win)
                return "Seal the chart at the stamping desk.";
            return (Page + 1) + "/" + region.charts.Length + "  ·  " + region.charts[Page] + "  ·  " +
                   region.rule;
        }
        public string Label(string id)
        {
            if (id.StartsWith("A_Key"))
                return Bearings[id[5] - '0'];
            if (id.StartsWith("A_Log"))
                return region.sites[id[5] - '0'];
            switch (id)
            {
            case "A_Stamp":
                return "Stamp the dispatch";
            case "A_Reset":
                return "Rewind chart";
            case "A_Hint":
                return "Navigator's notes";
            case "A_Talk":
                return region.guide;
            default:
                return "Way arch";
            }
        }
        public string Use(string id)
        {
            travel = null;
            if (id.StartsWith("A_Log"))
            {
                int i = id[5] - '0';
                logs |= 1 << i;
                return region.testimony[i];
            }
            if (id == "A_Talk")
                return Done ? region.ending : (logs == 0 ? region.intro : region.rule);
            if (Done)
                return region.ending;
            if (id == "A_Gate" || !Surveyed)
                return Objective();
            if (id == "A_Stamp")
            {
                if (!Piece.win)
                    return "The seal stays cold. " + Objective();
                sheet++;
                if (Done)
                    return region.ending;
                position = 0;
                return "Dispatch sealed. " + Objective();
            }
            if (id == "A_Hint")
                return Piece.win        ? Objective()
                       : Piece.hint < 0 ? "This cart is wedged. Use the rewind lever."
                                        : "From here, steer " + Bearings[Piece.hint] + ". " + region.rule;
            if (id == "A_Reset")
            {
                position = 0;
                return "This chart is back at its starting mark.";
            }
            if (!id.StartsWith("A_Key") || Piece.win)
                return Objective();
            int d = id[5] - '0', next = Piece.move[d];
            if (next == position)
                return "The way is blocked.";
            travel = Piece.paths == null || Piece.paths.Length <= d
                         ? ((char)(65 + Board.states[next].p)).ToString()
                         : Piece.paths[d];
            position = next;
            return Piece.win ? "The arrival ring answers. Stamp this dispatch."
                             : region.charts[Page] + "  ·  " + Bearings[d];
        }
    }
}
