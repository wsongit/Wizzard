// Run with the same Mono compiler and serializer as StoryGraph.cs.
using System;
using System.Web.Script.Serialization;
using Wizzard;

class SatchelCheck
{
    static void Require(bool ok,string message) { if(!ok) throw new Exception(message); }
    static void Main()
    {
        var json=new JavaScriptSerializer();
        var bag=new BellwakeSatchel();
        bag.Buy(0);bag.Buy(0);bag.Buy(1);bag.Buy(3);
        Require(bag.coins==0 && bag.sword && bag.shield && bag.pears==1,"Prices or duplicate purchases");
        bag.Buy(2);
        Require(!bag.staff && bag.coins==0,"Unfunded purchase");
        Require(!bag.Eat() && bag.pears==1,"Consumption at full health");
        bag.Cycle();Require(bag.equipped==3,"Equipping a pear");
        bag.hearts=2;Require(bag.Eat() && bag.hearts==3 && bag.pears==0 && bag.equipped==0,"Healing");
        for(int i=0;i<6;i++)
        {
            int before=bag.coins;
            bag.Reward(i);bag.Reward(i);
            bag=json.Deserialize<BellwakeSatchel>(json.Serialize(bag));
            bag.Reward(i);
            Require(bag.coins==before+(i%2==0?5:7),"Duplicate reward in district "+i);
        }
        bag.Buy(2);bag.minutes=1210;
        var saved=json.Deserialize<BellwakeSatchel>(json.Serialize(bag));
        Require(saved.staff && saved.equipped==2 && saved.coins==28 && saved.minutes==1210,"Save round trip");
        var fresh=new BellwakeSatchel();fresh.Cycle();
        Require(fresh.coins==12 && fresh.hearts==3 && fresh.equipped==0 && fresh.cleared==0,"Independent file");
        Console.WriteLine("PASS purchases, duplicate and unfunded sales, equipment, healing, six encounter rewards, save and independent file");
    }
}
