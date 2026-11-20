using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.XR;
using XRUsage = UnityEngine.XR.CommonUsages;

namespace Wizzard
{
    public sealed class BellwakeTitle : MonoBehaviour
    {
        enum Page { Loading, Files, Name, Settings, Prologue, Leaving }
        const string Alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ -";
        const string LegacyKey = "Wizzard.Bellwake.v1";
        static readonly int[] Volumes = { 0, 25, 50, 75, 100 };
        static readonly int[] Turns = { 30, 45, 60 };
        static readonly int[] Rates = { 36, 62, 95 };
        public static int LettersPerSecond => Rates[Setting("letters",1,Rates.Length)];
        static int Setting(string name,int fallback,int count) =>
            Mathf.Clamp(PlayerPrefs.GetInt("Bellwake.settings."+name,fallback),0,count-1);
        static void Set(string name,int value) { PlayerPrefs.SetInt("Bellwake.settings."+name,value); PlayerPrefs.Save(); }

        GorillaPlayer player;
        BellwakeDisplay card;
        Transform grove, moth, leftWing, rightWing, sleeper, stage;
        Quaternion leftRest, rightRest;
        Page page;
        int choice, slot, letter;
        string runner = "";
        float age, nextStep;
        int lastStick;
        bool triggerDown, backDown;
        Keyboard keyboard;
        Renderer[] rigPaint;
        Material sky;
        Texture2D plate;
        static string KeyFor(int i) => i==0 ? LegacyKey : LegacyKey+".file"+(i+1);
        string SaveKey => KeyFor(slot);
        string FileName(int i) => BellwakeCheckpoint.Exists(KeyFor(i)) ?
            PlayerPrefs.GetString("Bellwake.name."+i,"Returning runner") : "Empty file";

        public void Open(GorillaPlayer rig)
        {
            player=rig;
            player.MovementLocked=true;
            ApplySettings();
            rigPaint=rig.GetComponentsInChildren<Renderer>(true);
            foreach(var r in rigPaint) r.enabled=false;
            card=new BellwakeDisplay(rig.head);
            plate=Resources.Load<Texture2D>("Bellwake/Letters/BellrootDawn");
            ShowLoading("A lantern stirs beneath the sleeping bellroot…");
            keyboard=Keyboard.current;
            if(keyboard!=null) keyboard.onTextInput+=TypeName;
            StartCoroutine(LoadGrove());
        }
        void ShowLoading(string words)
        {
            card.Say("Bellwake   •   The sleeping bellroot",words);
            card.Survey(plate,null);
        }
        void ApplySettings()
        {
            AudioListener.volume=Volumes[Setting("volume",3,Volumes.Length)]/100f;
            player.turnAngle=Turns[Setting("turn",1,Turns.Length)];
            player.floorAssist=Setting("reach",1,2)==1;
        }
        IEnumerator LoadGrove()
        {
            yield return null;
            string[] models={"GroveBank","Bellroot","LanternMoth","Bellrunner","RunnerHead"};
            for(int i=0;i<models.Length;i++)
            {
                ShowLoading("Opening the grove   "+(i+1)+" / "+models.Length);
                yield return Resources.LoadAsync<GameObject>("Bellwake/Wayfarer/"+models[i]);
            }
            var panorama=Resources.LoadAsync<Cubemap>("Bellwake/Skies/Bellmarket");
            var stars=Resources.LoadAsync<Cubemap>("Bellwake/Skies/HillStars");
            yield return panorama;
            yield return stars;
            sky=new Material(Shader.Find("Wizzard/BellwakeSky"));
            sky.SetTexture("_Stars",stars.asset as Cubemap);
            BellwakeDaylight.SetPanorama(sky,panorama.asset as Cubemap);
            BellwakeDaylight.SetSkyClock(420f);
            RenderSettings.skybox=sky;
            player.head.GetComponent<Camera>().clearFlags=CameraClearFlags.Skybox;
            stage=new GameObject("Bellroot at first light").transform;
            Vector3 forward=Vector3.ProjectOnPlane(player.head.forward,Vector3.up).normalized;
            if(forward.sqrMagnitude<.1f) forward=Vector3.forward;
            Vector3 clearing = player.head.position + forward*3.85f;
            clearing.y = player.transform.position.y;
            stage.SetPositionAndRotation(clearing,Quaternion.LookRotation(forward));
            stage.localScale=Vector3.one*.86f;
            BellwakeModels.Wayfarer("GroveBank",stage);
            grove=BellwakeModels.Wayfarer("Bellroot",stage).transform;
            grove.localPosition=new Vector3(-.90f,0,.3f);
            grove.localScale=Vector3.one*.69f;
            sleeper=BellwakeModels.Wayfarer("Bellrunner",stage).transform;
            sleeper.localPosition=new Vector3(.85f,.23f,-.55f);
            sleeper.localRotation=Quaternion.Euler(0,150,-58);
            var face=BellwakeModels.Wayfarer("RunnerHead",sleeper).transform;
            face.localPosition=Vector3.up*.13f;
            foreach(int side in new[]{-1,1})
            {
                Vector3 shoulder=new Vector3(side*.18f,.12f,0);
                Vector3 wrist=new Vector3(side*.24f,-.18f,.095f);
                var arm=BellwakeModels.Create("RunnerArm",sleeper).transform;
                arm.localPosition=(shoulder+wrist)*.5f;
                arm.localRotation=Quaternion.FromToRotation(Vector3.up,shoulder-wrist);
                arm.localScale=new Vector3(.8f,Vector3.Distance(shoulder,wrist),.8f);
                var hand=BellwakeModels.Create(side<0?"LeftPalm":"RightPalm",sleeper).transform;
                hand.localPosition=wrist;
                hand.localScale=Vector3.one*.80f;
            }
            moth=BellwakeModels.Wayfarer("LanternMoth",stage).transform;
            foreach(var wing in moth.GetComponentsInChildren<Transform>())
            {
                if(wing.name=="LeftWing") {leftWing=wing;leftRest=wing.localRotation;}
                if(wing.name=="RightWing") {rightWing=wing;rightRest=wing.localRotation;}
            }
            page=Page.Files;
            choice=Mathf.Clamp(PlayerPrefs.GetInt("Bellwake.lastFile",0),0,2);
            Draw();
        }
        void Update()
        {
            if(page==Page.Leaving || page==Page.Loading) return;
            age+=Time.unscaledDeltaTime;
            bool ok=Pressed(XRUsage.triggerButton,ref triggerDown) ||
                (keyboard!=null && (keyboard.enterKey.wasPressedThisFrame ||
                    (page!=Page.Name && keyboard.eKey.wasPressedThisFrame)));
            bool back=Pressed(XRUsage.secondaryButton,ref backDown) || (keyboard!=null && keyboard.escapeKey.wasPressedThisFrame);
            float flap=35*Mathf.Sin(age*22);
            if(leftWing) leftWing.localRotation=Quaternion.AngleAxis(flap,Vector3.forward)*leftRest;
            if(rightWing) rightWing.localRotation=Quaternion.AngleAxis(-flap,Vector3.forward)*rightRest;
            Vector3 nest=new Vector3(-.72f,1.51f,-.45f);
            float t=page==Page.Prologue ? Mathf.SmoothStep(0,1,(age-2)/4f) : 0;
            moth.localPosition=Vector3.Lerp(nest,new Vector3(.82f,.64f,-.65f),t)+new Vector3(.14f*Mathf.Sin(age*3),.07f*Mathf.Cos(age*4)+.45f*Mathf.Sin(t*Mathf.PI),0);
            if(page==Page.Prologue)
            {
                float wake=Mathf.SmoothStep(0,1,(age-5.5f)/1.7f);
                sleeper.localRotation=Quaternion.Euler(0,150,Mathf.Lerp(-58,0,wake));
                sleeper.localPosition=new Vector3(.85f,Mathf.Lerp(.23f,.37f,wake),-.55f);
                if(choice==0 && age>=3) {choice=1;card.Say("Pip, the lantern moth","A little light slips from the branches and finds a sleeping bellrunner.");}
                if(choice==1 && age>=6.3f) {choice=2;card.Say("Pip","Wake up, "+runner+"! The river rang the bell, and nobody pulled the rope.");}
                if(age>=10 || (ok && age>.45f)) Launch();
                return;
            }
            int step=Step();
            if(page==Page.Files)
            {
                if(step!=0) { choice=Wrap(choice+step,4); Draw(); }
                if(!ok) return;
                if(choice==3) {page=Page.Settings;choice=0;Draw();return;}
                slot=choice;
                if(BellwakeCheckpoint.Exists(SaveKey)) {runner=FileName(slot);Launch();return;}
                runner="";letter=0;page=Page.Name;Draw();return;
            }
            if(back) { page=Page.Files; choice=slot; Draw(); return; }
            if(page==Page.Name)
            {
                if(step!=0) {letter=Wrap(letter+step,Alphabet.Length+2);Draw();}
                if(keyboard!=null && keyboard.backspaceKey.wasPressedThisFrame) Erase();
                if(!ok) return;
                if((keyboard!=null && keyboard.enterKey.wasPressedThisFrame) || letter==Alphabet.Length+1)
                {
                    runner=runner.Trim();
                    if(runner.Length==0){Draw();return;}
                    page=Page.Prologue;age=0;choice=0;
                    card.Say("The sleeping bellroot","Before the market wakes, the oldest tree in the valley hears a note buried under its roots.  •  E / trigger to skip");
                }
                else if(letter==Alphabet.Length) Erase();
                else if(runner.Length<12) {runner+=Alphabet[letter]; Draw();}
                return;
            }
            if(step!=0){choice=Wrap(choice+step,5);Draw();}
            if(!ok) return;
            switch(choice)
            {
                case 0:Set("volume",Wrap(Setting("volume",3,5)+1,5));break;
                case 1:Set("turn",Wrap(Setting("turn",1,3)+1,3));break;
                case 2:Set("letters",Wrap(Setting("letters",1,3)+1,3));break;
                case 3:Set("reach",1-Setting("reach",1,2));break;
                default:page=Page.Files;choice=slot;break;
            }
            ApplySettings();Draw();
        }
        void Erase(){if(runner.Length>0) runner=runner.Substring(0,runner.Length-1); Draw();}
        void TypeName(char c)
        {
            if(page!=Page.Name || runner.Length>=12 || !(char.IsLetterOrDigit(c)||c==' '||c=='-')) return;
            runner+=c;Draw();
        }
        static int Wrap(int v,int count)=>(v+count)%count;
        static bool Pressed(InputFeatureUsage<bool> usage,ref bool previous)
        {
            bool down=false;
            foreach(var node in Controllers)
                if(InputDevices.GetDeviceAtXRNode(node).TryGetFeatureValue(usage,out bool on)) down|=on;
            bool result=down&&!previous;previous=down;return result;
        }
        static readonly XRNode[] Controllers={XRNode.LeftHand,XRNode.RightHand};
        int Step()
        {
            if(keyboard!=null)
            {
                if(keyboard.leftArrowKey.wasPressedThisFrame) return -1;
                if(keyboard.rightArrowKey.wasPressedThisFrame) return 1;
            }
            float x=0;
            foreach(var node in Controllers)
                if(InputDevices.GetDeviceAtXRNode(node).TryGetFeatureValue(XRUsage.primary2DAxis,out Vector2 v)&&Mathf.Abs(v.x)>Mathf.Abs(x))x=v.x;
            int d=Mathf.Abs(x)>.55f?(x>0?1:-1):0;
            if(d==0){lastStick=0;return 0;}
            if(d==lastStick && Time.unscaledTime<nextStep)return 0;
            nextStep=Time.unscaledTime+(d==lastStick?.14f:.40f);lastStick=d;return d;
        }
        void Draw()
        {
            const string nav="Left / right to browse. Trigger or Enter selects.";
            if(page==Page.Files) card.Say("Bellwake   •   Choose a journey",
                (choice==3?"‹  Settings  ›":"‹  File "+(choice+1)+"   ·   "+FileName(choice)+"  ›")+"\n"+nav);
            else if(page==Page.Name) card.Say("Name your bellrunner   •   "+(runner.Length==0?"_":runner),
                "‹  "+(letter==Alphabet.Length?"Erase":letter==Alphabet.Length+1?"Begin":Alphabet[letter].ToString())+"  ›   •   Select letters, then Begin. On PC type your name and press Enter.");
            else card.Say("Bellwake   •   Settings", "‹  "+new[]{"Volume   "+Mathf.RoundToInt(AudioListener.volume*100)+"%",
                "Snap turn   "+player.turnAngle+"°","Dialogue   "+LettersPerSecond+" letters/sec",
                "Floor reach assist   "+(player.floorAssist?"On":"Off"),"Return to files"}[choice]+"  ›\n"+nav);
        }
        void Launch()
        {
            page=Page.Leaving;
            if (!BellwakeCheckpoint.Exists(SaveKey))
            {
                PlayerPrefs.SetString("Bellwake.name."+slot,runner);
                var firstCheckpoint=new BellwakeJourney { satchel=new BellwakeSatchel() };
                BellwakeCheckpoint.Write(SaveKey, JsonUtility.ToJson(firstCheckpoint), null);
            }
            PlayerPrefs.SetInt("Bellwake.lastFile",slot);PlayerPrefs.Save();
            Destroy(stage.gameObject);
            foreach(var r in rigPaint) if(r) r.enabled=true;
            ShowLoading("Opening your road book, "+runner+"…");
            card.SetQueue(4980);
            var campaign=gameObject.AddComponent<BellwakeCampaign>();
            campaign.Initialize(player,SaveKey);
            StartCoroutine(FinishOpening(campaign));
        }
        IEnumerator FinishOpening(BellwakeCampaign campaign)
        {
            yield return null;
            while(!campaign.OpeningReady) yield return null;
            Destroy(this);
        }
        void OnDestroy()
        {
            if(keyboard!=null)keyboard.onTextInput-=TypeName;
            if(card!=null)card.Dispose();
            if(sky!=null)Destroy(sky);
            if(stage!=null)Destroy(stage.gameObject);
        }
    }
}
