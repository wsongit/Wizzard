using System;

namespace Wizzard
{
    [Serializable]
    public sealed class BellwakeSatchel
    {
        public int coins = 12, hearts = 3, pears, equipped, cleared;
        public bool sword, shield, staff;
        public float minutes = 420;
        public static readonly string[] Goods = { "Toll sword", "Ferry shield", "Reed staff", "Honey pear" };
        public static readonly int[] Prices = { 6, 4, 8, 2 };
        public bool Owns(int item) => item == 0 ? sword : item == 1 ? shield : item == 2 ? staff : pears>0;
        public string Buy(int item)
        {
            if (item != 3 && Owns(item)) return "You already carry the "+Goods[item].ToLowerInvariant()+".";
            if (coins < Prices[item]) return "You need "+(Prices[item]-coins)+" more ferry marks.";
            coins -= Prices[item];
            if (item==0) { sword=true; equipped=1; }
            else if (item==1) shield=true;
            else if (item==2) { staff=true; equipped=2; }
            else { pears++; if(equipped==0) equipped=3; }
            return "Packed "+Goods[item].ToLowerInvariant()+".";
        }
        public void Cycle()
        {
            do { equipped=(equipped+1)%4; }
            while ((equipped==1&&!sword)||(equipped==2&&!staff)||(equipped==3&&pears==0));
        }
        public bool Eat()
        {
            if (pears<=0 || hearts>=3) return false;
            hearts++; pears--;
            if(pears==0 && equipped==3) Cycle();
            return true;
        }
        public void Reward(int district)
        {
            int bit=1<<district;
            if((cleared & bit)!=0)return;
            cleared|=bit; coins+=district%2==0?5:7;
        }
    }
}
