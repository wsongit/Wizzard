// Run the native rules without rendering. Compares every hint with a shorter route to a delivery.
using System;
using System.IO;
using System.Web.Script.Serialization;
using Wizzard;

class PassageCheck
{
    static void Check(bool condition, string message)
    {
        if (!condition)
            throw new Exception(message);
    }
    static void Main(string[] args)
    {
        var read = new JavaScriptSerializer { MaxJsonLength = 16000000 };
        var atlas = read.Deserialize<PassageAtlas>(File.ReadAllText(Path.Combine(args[0], "Passages.json")));
        int total = 0, steps = 0;
        foreach (var region in atlas.regions)
        {
            var book = read.Deserialize<PassageBook>(
                File.ReadAllText(Path.Combine(args[0], "Charts", region.key + ".json")));
            var route = new BellwakePassage { active = true };
            route.Bind(region, book);
            Check(!route.Surveyed && route.Use("A_Key0") == route.Objective(), region.key + " evidence gate");
            for (int sheet = 0; sheet < book.boards.Length; sheet++)
            {
                var b = book.boards[sheet];
                route.Use("A_Log" + (sheet / 3));
                for (int i = 0; i < b.states.Length; i++)
                {
                    route.position = i;
                    var original = route.Piece;
                    Check(original.move.Length == 4 && original.p >= 0 && original.p < 49, "invalid position");
                    for (int k = 0; k < 4; k++)
                    {
                        route.position = i;
                        route.Use("A_Key" + k);
                        Check(route.position == original.move[k], "wrong action");
                    }
                    route.position = i;
                    if (original.hint < 0 && !original.win)
                        route.Use("A_Reset");
                    int n = 0;
                    while (!route.Piece.win)
                    {
                        int d = route.Piece.hint;
                        Check(d >= 0 && d < 4 && ++n <= b.states.Length, "unreachable delivery");
                        route.Use("A_Key" + d);
                    }
                    if (i == 0)
                    {
                        Check(n == b.par, "wrong initial distance");
                        steps += n;
                    }
                }
                total += b.states.Length;
                route.Use("A_Stamp");
                Check(route.sheet == sheet + 1, "missing dispatch");
            }
            Check(route.Done && route.logs == 7, "missing witness");
            route.Leave();
            Check(!route.active && route.book == null && route.region == null, "stale booklet");
        }
        Console.WriteLine(total + " positions, four directions checked at every position, " + steps +
                          " minimum moves across all charts");
    }
}
