using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.XR;
using XRUsage = UnityEngine.XR.CommonUsages;

namespace Wizzard
{
    public sealed class BellwakeCampaign : MonoBehaviour
    {
        const string SaveKey = "Wizzard.Bellwake.v1";
        const string Path = "Bellwake/";
        static readonly string[] Tones = { "Leaf", "Ember", "Tide" };
        static readonly string[] Horizon = { "D3BB93", "A4B890", "AEC4B6", "BA917B", "908BA6" };
        readonly Dictionary<string, Transform> nodes = new Dictionary<string, Transform>();
        readonly Dictionary<string, TextMesh> points = new Dictionary<string, TextMesh>();
        readonly Dictionary<string, Material> paints = new Dictionary<string, Material>();
        readonly Dictionary<string, Quaternion> rest = new Dictionary<string, Quaternion>();
        readonly XrPress use = new XrPress(), journal = new XrPress(), whistle = new XrPress();
        BellwakeJourney story;
        PassageAtlas atlas;
        WorksPlan worksPlan;
        WorksStation observation;
        float voyageFraction;
        bool InWorks => story.works!=null && story.works.active;
        WorksVisual[] fixtures=Array.Empty<WorksVisual>();
        Vector3[] fixtureLocations;
        Vector3 railAxis;
        readonly float[] drumAngles=new float[3];
        Quaternion[] fixtureAngles;
        BellwakePassage Route => story.passage;
        bool InPassage => Route != null && Route.active;
        bool HasFloodBook => !InWorks && (story.room == 4 || story.ending != 0) && story.works.Remembered(worksPlan,"landed");
        float RoomRadius => InWorks && story.works.Room.halfSpan > 0 ? story.works.Room.halfSpan : 20f;
        string RoomTitle => InWorks ? story.works.Room.title : InPassage ? Route.region.title : BellwakeJourney.Titles[story.room];
        string Objective => InWorks ? story.works.Objective() : InPassage ? Route.Objective() : story.Objective();
        BellwakeDisplay display;
        GorillaPlayer player;
        GameObject set, meadow, sign;
        MossbellVillage village;
        AudioSource score, notes;
        readonly AudioClip[] chimes = new AudioClip[4];
        Material sky, curtain;
        Renderer curtainRenderer;
        Camera cam;
        string focus, lastHint, savedCheckpoint;
        Transform struck;
        Quaternion strikeRest;
        Vector3 waveScale;
        float strikeAt, gestureUntil;
        int lastSecond = -1;
        float messageUntil, pulseUntil, restartUntil, cameraCheck;
        bool loading, outdoors, journalOpen;
        int journalPage, roadPage;
        BellwakeFrameSample profiler;
        Vector3 spawn;
        Quaternion facing;

        sealed class XrPress
        {
            bool previous;
            public bool Read(InputFeatureUsage<bool> usage, bool leftOnly = false)
            {
                var left = InputDevices.GetDeviceAtXRNode(XRNode.LeftHand);
                var right = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);
                bool down = (left.TryGetFeatureValue(usage, out bool a) && a) ||
                            (!leftOnly && right.TryGetFeatureValue(usage, out bool b) && b);
                bool pressed = down && !previous;
                previous = down;
                return pressed;
            }
        }
        public void Initialize(GorillaPlayer rig)
        {
            player = rig;
            cam = rig.head.GetComponent<Camera>();
            display = new BellwakeDisplay(rig.head);
            story = Restore();
            atlas = JsonUtility.FromJson<PassageAtlas>(Resources.Load<TextAsset>(Path + "Passages").text);
            worksPlan=JsonUtility.FromJson<WorksPlan>(Resources.Load<TextAsset>(Path+"Underworks").text);
            PrepareRoute();
            if (Debug.isDebugBuild)
            {
                profiler = gameObject.AddComponent<BellwakeFrameSample>();
                profiler.enabled = false;
            }
            sky = new Material(Shader.Find("Wizzard/BellwakeSky"));
            score = gameObject.AddComponent<AudioSource>();
            score.loop = true;
            score.playOnAwake = false;
            score.volume = .32f;
            notes = gameObject.AddComponent<AudioSource>();
            notes.playOnAwake = false;
            notes.volume = .57f;
            for (int i = 0; i < 4; i++)
                chimes[i] = Resources.Load<AudioClip>(Path + "Audio/" + (i == 3 ? "Toll" : Tones[i]));
            var cover = GameObject.CreatePrimitive(PrimitiveType.Quad);
            Destroy(cover.GetComponent<Collider>());
            cover.transform.SetParent(rig.head, false);
            cover.transform.localPosition = Vector3.forward * .3f;
            cover.transform.localScale = Vector3.one * 5;
            curtain = new Material(Shader.Find("Wizzard/VillageFade"));
            curtain.renderQueue = 4950;
            curtainRenderer = cover.GetComponent<Renderer>();
            curtainRenderer.sharedMaterial = curtain;
            curtainRenderer.enabled = false;
            StartCoroutine(EnterRoom());
        }
        void PrepareRoute()
        {
            if (Route == null) story.passage = new BellwakePassage();
            if(story.works==null) story.works=new BellwakeWorks();
            int savedChamber=story.works.chamber;
            bool early=savedChamber>=0 && savedChamber<worksPlan.rooms.Length && worksPlan.rooms[savedChamber].early;
            if(early ? story.room!=1 || story.ending!=0 : story.room!=3 || !story.Solved) story.works.active=false;
            story.works.Bind(worksPlan);
            int slots=BellwakeJourney.Rooms.Length+atlas.regions.Length+1+worksPlan.rooms.Length;
            if (story.secondsByPlace==null || story.secondsByPlace.Length<slots)
                Array.Resize(ref story.secondsByPlace, slots);
            Route.completed = Mathf.Clamp(Mathf.Max(Route.completed,story.room),0,atlas.regions.Length);
            if (Route.completed != story.room || story.ending != 0 || story.room >= atlas.regions.Length)
                Route.active=false;
        }
        static BellwakeJourney Restore()
        {
            if (PlayerPrefs.HasKey(SaveKey))
                try
                {
                    var data = JsonUtility.FromJson<BellwakeJourney>(PlayerPrefs.GetString(SaveKey));
                    if (data != null && data.Valid())
                        return data;
                }
                catch (ArgumentException)
                {
                    Debug.LogWarning("Bellwake could not read the saved checkpoint.");
                }
            return new BellwakeJourney();
        }
        bool checkingTravel;
        void Save()
        {
            if (checkingTravel) return;
            string checkpoint = JsonUtility.ToJson(story);
            if (checkpoint == savedCheckpoint)
                return;
            PlayerPrefs.SetString(SaveKey, checkpoint);
            PlayerPrefs.Save();
            savedCheckpoint = checkpoint;
        }
        void Say(string title, string words, float seconds = 11f)
        {
            lastHint = null;
            messageUntil = Time.unscaledTime + seconds;
            display.Say(title, words);
        }
        IEnumerator Fade(float from, float to)
        {
            curtainRenderer.enabled = true;
            for (float t = 0; t < .24f; t += Time.unscaledDeltaTime)
            {
                curtain.color = new Color(0, 0, 0, Mathf.Lerp(from, to, t / .24f));
                yield return null;
            }
            curtain.color = new Color(0, 0, 0, to);
            curtainRenderer.enabled = to > 0;
        }
        IEnumerator ReleaseArea(string nextMusic=null)
        {
            guide = null;
            flight.Clear();
            display.ClearSurvey();
            fixtures=Array.Empty<WorksVisual>();
            observation=null;
            roadPage=0;
            movingTrail = null;
            focus = lastHint = null;
            struck = null;
            if (Route != null) { Route.book = null; Route.region = null; }
            nodes.Clear();
            points.Clear();
            rest.Clear();
            if(score.clip!=null && score.clip.name!=nextMusic)
            {
                score.Stop();
                score.clip=null;
            }
            sky.SetTexture("_Panorama", null);
            if (set != null) { set.SetActive(false); Destroy(set); set = null; }
            if (village != null) { village.enabled = false; Destroy(village); village = null; }
            if (meadow != null) { meadow.SetActive(false); Destroy(meadow); meadow = null; sign = null; }
            foreach (var material in paints.Values) Destroy(material);
            paints.Clear();
            // Destroy is deferred until the frame ends. Drop references before the engine sweep.
            yield return null;
            yield return Resources.UnloadUnusedAssets();
        }
        IEnumerator EnterRoom()
        {
            loading = true;
            if (profiler != null)
                profiler.StartTravel();
            player.MovementLocked = true;
            journalOpen = false;
            focus = null;
            struck = null;
            try
            {
                yield return Fade(0, 1);
                PrepareRoute();
                string key = InWorks ? story.works.Room.key : InPassage ? atlas.regions[story.room].key : BellwakeJourney.Rooms[story.room];
                bool dawn = story.ending != 0;
                string theme = dawn ? "Morning" : InWorks ? story.works.Room.theme : key;
                yield return ReleaseArea(theme);
                if (InPassage)
                {
                    var charts=Resources.LoadAsync<TextAsset>(Path+"Charts/"+key);
                    yield return charts;
                    Route.Bind(atlas.regions[story.room],JsonUtility.FromJson<PassageBook>(((TextAsset)charts.asset).text));
                }
                var request = Resources.LoadAsync<GameObject>(Path + "Rooms/" + key);
                yield return request;
                if (request.asset == null)
                    throw new InvalidOperationException("Missing Bellwake room " + key);
                outdoors = false;
                set = Instantiate((GameObject)request.asset);
                set.name = key;
                float sliceStart = Time.realtimeSinceStartup;
                foreach (var t in set.GetComponentsInChildren<Transform>(true))
                {
                    if (Time.realtimeSinceStartup - sliceStart >= .003f)
                    {
                        yield return null;
                        sliceStart = Time.realtimeSinceStartup;
                    }
                    nodes[t.name] = t;
                    if (t.name.StartsWith("Rotor") || t.name == "GreatBell" || t.name == "Familiar" ||
                        t.name.StartsWith("Speaker"))
                        rest[t.name] = t.rotation;
                    if (t.name == "HushWave")
                        waveScale = t.localScale;
                    var r = t.GetComponent<MeshRenderer>();
                    if (r == null)
                        continue;
                    if (t.name == "C_Solids")
                        r.enabled = false;
                    else
                        Paint(r);
                    if (t.name == "Terrain" || t.name == "Rim" || t.name == "Set" || t.name == "C_Solids")
                    {
                        t.gameObject.layer = MeadowWorld.GroundLayer;
                        t.gameObject.AddComponent<MeshCollider>().sharedMesh =
                            t.GetComponent<MeshFilter>().sharedMesh;
                    }
                }
                foreach (var pair in nodes)
                    if (pair.Key.StartsWith("A_"))
                        points.Add(pair.Key, display.Label(pair.Value, Label(pair.Key)));
                spawn = nodes["Spawn"].position;
                var dir = nodes["Look"].position - spawn;
                dir.y = 0;
                facing = Quaternion.LookRotation(dir);
                spawn = Arrival();
                if (InWorks && story.works.Room.early) PrepareGuide();
                var panorama = Resources.LoadAsync<Cubemap>(Path + "Skies/" + theme);
                var song = score.clip==null ? Resources.LoadAsync<AudioClip>(Path + "Audio/" + theme) : null;
                yield return panorama;
                ApplyLook((Cubemap)panorama.asset);
                if(InWorks)
                {
                    fixtures=story.works.Room.visuals;
                    if (nodes.TryGetValue("RailStart",out var railStart))
                        railAxis=(nodes["RailEnd"].position-railStart.position).normalized;
                    fixtureLocations=Array.ConvertAll(fixtures,v=>nodes[v.node].position);
                    fixtureAngles=Array.ConvertAll(fixtures,v=>nodes[v.node].rotation);
                    if (nodes.TryGetValue("Drum",out var drum))
                    {
                        Vector3 axis=nodes["Bearing0"].position-drum.position;
                        for(int j=0;j<3;j++)
                            drumAngles[j]=Vector3.SignedAngle(axis,nodes["Bearing"+j].position-drum.position,Vector3.up);
                    }
                    AnimateWorks(true);
                }
                Sync();
                player.Teleport(spawn, facing);
                Physics.SyncTransforms();
                if(song!=null)
                {
                    yield return song;
                    score.clip=(AudioClip)song.asset;
                    score.Play();
                }
                pulseUntil = Time.unscaledTime + 32;
                Save();
                Say(dawn ? "BELLWAKE  /  EPILOGUE" : "BELLWAKE  /  " + RoomTitle,
                    dawn ? (story.ending == 1 ? "The long watch is over. For the first time, the whole market " +
                                                "takes its turn at " +
                                                    "the bell."
                                              : "At dawn the river sings with a human voice. Tavi has set two " +
                                                "places for breakfast.")
                    : InPassage || InWorks ? Objective
                    : story.room == 0 && !story.commissioned
                        ? "The morning bell failed to ring. Find Tavi on the path. Look at her and press E or a " +
                              "controller trigger."
                        : "Chapter " + (story.room == 0 ? "home" : story.room.ToString()) + "   /   " +
                              story.Objective(),
                    8);
                yield return Fade(1, 0);
                if (profiler != null)
                    profiler.Begin(key);
            }
            finally
            {
                loading = false;
                player.MovementLocked = false;
                curtainRenderer.enabled = false;
            }
        }
        void Paint(Renderer renderer)
        {
            var slots = renderer.sharedMaterials;
            for (int i = 0; i < slots.Length; i++)
            {
                if (slots[i] == null)
                    continue;
                string name = slots[i].name;
                if (!paints.TryGetValue(name, out var mat))
                {
                    var tile = Resources.Load<Texture2D>(Path + "Textures/" + name);
                    if (tile == null)
                        throw new InvalidOperationException("Unmapped Bellwake paint " + name);
                    mat = new Material(Shader.Find("Wizzard/BellwakePaint")) { name = name, mainTexture = tile };
                    if (name == "SeaGlass" || name == "Amber")
                        mat.SetFloat("_Glow", .88f);
                    paints.Add(name, mat);
                }
                slots[i] = mat;
            }
            renderer.sharedMaterials = slots;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        }
        Vector3 Arrival()
        {
            string camp = InWorks ? story.works.camp : null;
            return !string.IsNullOrEmpty(camp) && camp.StartsWith("Rest") && nodes.TryGetValue(camp,out var at)
                ? at.position : nodes["Spawn"].position;
        }
        void ApplyLook(Cubemap panorama)
        {
            int r = story.room;
            ColorUtility.TryParseHtmlString("#" + Horizon[r], out Color horizon);
            if (story.ending != 0)
                horizon = new Color(.94f, .79f, .61f);
            if (InWorks && !string.IsNullOrEmpty(story.works.Room.fog)) ColorUtility.TryParseHtmlString(story.works.Room.fog,out horizon);
            if (InWorks && story.works.Room.key == "Wrenfall") ColorUtility.TryParseHtmlString("#b7d2c2", out horizon);
            sky.SetTexture("_Panorama", panorama);
            RenderSettings.skybox = sky;
            cam.clearFlags = CameraClearFlags.Skybox;
            RenderSettings.fog = true;
            RenderSettings.fogColor = horizon;
            RenderSettings.fogStartDistance = RoomRadius * .9f;
            RenderSettings.fogEndDistance = RoomRadius * 3.4f;
        }
        string Label(string id)
        {
            if (InWorks) return story.works.Station(id).label;
            if (InPassage) return Route.Label(id);
            switch (id)
            {
            case "A_Talk":
                return story.room == 4 && story.strikes == 3 ? "Ina" : BellwakeJourney.Speakers[story.room];
            case "A_Ina":
                return "Ina";
            case "A_RoadBook": return "Letters from the public road";
            case "A_Nameplate": return "Fourth hand";
            case "A_Roster":
                return "Watch roster";
            case "A_Letter":
                return "Witness leaf";
            case "A_Gate":
                return story.ending != 0 ? "Begin again" : "Way arch";
            case "A_Meadow":
                return "Long Meadow";
            case "A_End0":
                return "Share the watch";
            case "A_End1":
                return "Free the voice";
            case "A_Lens":
                return "Casting cup";
            default:
                return story.KeyName(id[id.Length - 1] - '0');
            }
        }
        static void Active(Transform t, bool active)
        {
            if (t.gameObject.activeSelf != active)
                t.gameObject.SetActive(active);
        }
        void Toggle(string id, bool active)
        {
            if (nodes.TryGetValue(id, out var t))
                Active(t, active);
        }
        Vector3 trailStart;
        float trailTime;
        string movingTrail;
        Vector3 ChartPoint(int tile)
        {
            Vector3 nw=nodes["NW"].position;
            return nw + (nodes["NE"].position-nw)*(tile%7/6f) + (nodes["SW"].position-nw)*(tile/7/6f);
        }
        void AnimateWorks(bool snap)
        {
            float mix=snap?1:1-Mathf.Exp(-Time.deltaTime*8);
            for(int i=0;i<fixtures.Length;i++)
            {
                var v=fixtures[i];var t=nodes[v.node];int n=story.works.Signal(v.signal);
                if(v.kind=="show") { Active(t,n==v.match && (v.node!="CrewAshore" || voyageFraction>=1)); continue; }
                if (v.kind=="pointer")
                {
                    t.rotation=Quaternion.Slerp(t.rotation,Quaternion.AngleAxis(drumAngles[n],Vector3.up)*fixtureAngles[i],mix);
                    continue;
                }
                if (v.kind=="slide")
                {
                    if (!string.IsNullOrEmpty(v.visibleSignal)) Active(t,story.works.Signal(v.visibleSignal)!=0);
                    float height=string.IsNullOrEmpty(v.stack) ? 0 : v.rise*story.works.Signal(v.stack);
                    var target=fixtureLocations[i]+railAxis*(v.amount*n)+Vector3.up*height;
                    t.position=Vector3.Lerp(t.position,target,mix);
                    continue;
                }
                if (v.kind == "voyage")
                {
                    voyageFraction = snap ? n : Mathf.MoveTowards(voyageFraction,n,Time.deltaTime/v.amount);
                    Vector3 turn = nodes[v.node+"Turn"].position;
                    Vector3 from = Vector3.Lerp(fixtureLocations[i],turn,voyageFraction);
                    Vector3 to = Vector3.Lerp(turn,nodes[v.node+"Berth"].position,voyageFraction);
                    t.position = Vector3.Lerp(from,to,voyageFraction);
                    continue;
                }
                if(v.kind=="lift") t.position=Vector3.Lerp(t.position,fixtureLocations[i]+Vector3.up*(v.amount*n),mix);
                else
                {
                    Vector3 axis=v.kind=="turn"?Vector3.up:facing*Vector3.forward;
                    t.rotation=Quaternion.Slerp(t.rotation,Quaternion.AngleAxis(n*v.amount,axis)*fixtureAngles[i],mix);
                }
            }
        }
        void Sync()
        {
            if(InWorks) { AnimateWorks(false); return; }
            if (InPassage)
            {
                int page=Route.Page;
                var paint=paints[Route.region.key+"Chart"];
                paint.mainTextureScale=new Vector2(1f/3,1f/3);
                paint.mainTextureOffset=new Vector2(page%3/3f,(2-page/3)/3f);
                nodes["Pawn"].position=ChartPoint(Route.Piece.p);
                Toggle("Cargo",Route.Piece.c>=0);
                if (Route.Piece.c>=0) nodes["Cargo"].position=ChartPoint(Route.Piece.c);
                Toggle("GateLight",Route.Done);
                return;
            }
            bool memorial=story.ending!=0 && story.works.Remembered(worksPlan,"named");
            bool publicRoad = story.ending!=0 && story.works.Signal("RainCourtArch")==1;
            Toggle("RoadBook",publicRoad);
            Toggle("A_RoadBook",publicRoad);
            Toggle("NightRoll",memorial);Toggle("A_Nameplate",memorial);
            bool gate = story.room == 0 ? story.commissioned : story.Solved && story.room < 4;
            Toggle("GateLight", gate);
            Toggle("Ina", story.ending == 2);
            Toggle("A_Ina", story.ending == 2);
            Toggle("Roster", story.ending == 1);
            Toggle("A_Roster", story.ending == 1);
            Toggle("HushWave", story.room == 4 && story.challenged && !story.Solved);
            for (int i = 0; i < 3; i++)
            {
                Toggle("Stray" + i, story.BeamCount == i + 1);
                Toggle("Call" + i, story.room == 4 && story.challenged && !story.Solved && story.CalledKey == i);
                Toggle("Flow" + i, (story.water & (1 << i)) != 0);
                Toggle("Choice" + i, story.room == 4 && story.strikes == 3);
                Toggle("A_End" + i, story.room == 4 && story.strikes == 3);
                if (story.room == 3)
                {
                    var t = nodes["Rotor" + i];
                    bool changed = (story.lenses & (1 << i)) != 0;
                    // Lenses 1 and 2 initially deflect outward. The last starts aimed away too.
                    bool quarter = !changed;
                    t.rotation = Quaternion.AngleAxis(quarter ? 90 : 0, Vector3.up) * rest[t.name];
                }
            }
            for (int i = 0; i < 4; i++)
                Toggle("Ray" + i, i < story.BeamCount);
            if (story.room == 4)
            {
                Toggle("A_Gate", false);
                points["A_Talk"].text = Label("A_Talk");
            }
        }
        void Update()
        {
            if (player == null || loading || checkingTravel || player.MovementLocked)
                return;
            if (Application.isFocused && !journalOpen && story.ending==0 && Time.unscaledDeltaTime<1)
            {
                int slot=outdoors ? BellwakeJourney.Rooms.Length+atlas.regions.Length :
                    InWorks ? BellwakeJourney.Rooms.Length+atlas.regions.Length+1+story.works.chamber :
                    InPassage ? BellwakeJourney.Rooms.Length+story.room : story.room;
                story.secondsByPlace[slot]+=Time.unscaledDeltaTime;
            }
            bool action = use.Read(XRUsage.triggerButton) ||
                          (Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame);
            bool book = journal.Read(XRUsage.primaryButton) ||
                        (Keyboard.current != null && Keyboard.current.jKey.wasPressedThisFrame);
            bool call = whistle.Read(XRUsage.gripButton, true) ||
                        (Keyboard.current != null && Keyboard.current.qKey.wasPressedThisFrame);
            if (outdoors)
            {
                if (sign == null || !sign.activeInHierarchy ||
                    Vector3.Distance(player.head.position, sign.transform.position + Vector3.up) > 4.3f)
                {
                    if (lastHint == "trail")
                    {
                        display.Hide();
                        lastHint = null;
                    }
                    return;
                }
                if (lastHint != "trail")
                {
                    display.Say("Bellmarket trail", "Press E or a trigger to return to Bellwake.");
                    lastHint = "trail";
                }
                if (action)
                    StartCoroutine(EnterRoom());
                return;
            }
            if (set == null)
                return;
            if (book)
            {
                journalOpen = !journalOpen;
                if (!journalOpen) display.ClearSurvey();
                observation = null;
                lastHint = null;
                messageUntil = 0;
                if (journalOpen)
                {
                    journalPage = -1;
                    ShowBook();
                }
            }
            if (journalOpen)
            {
                pulseUntil += Time.unscaledDeltaTime;
                if (action)
                {
                    do
                    {
                        journalPage++;
                    } while (journalPage < 5 && (story.letters & (1 << journalPage)) == 0);
                    if (journalPage == 5 && (!InWorks || story.works.Room.early)) journalPage++;
                    if (journalPage > 6 || (journalPage == 6 && !HasFloodBook))
                        journalPage = -1;
                    ShowBook();
                }
                return;
            }
            if (guide != null) { if (call) CallGuide(); FlyGuide(); }
            FindFocus();
            AnimateSet();
            float now = Time.unscaledTime;
            if (action && focus != null)
            {
                Interact(focus);
                return;
            }
            if (story.room == 4 && story.challenged && !story.Solved && now >= pulseUntil)
            {
                var line = story.Miss();
                notes.PlayOneShot(chimes[3]);
                pulseUntil = now + 24;
                Sync();
                Save();
                Say("The hollow toll", line, 5);
            }
            if (now >= messageUntil)
            {
                bool fighting = story.room == 4 && story.challenged && !story.Solved;
                string id = focus ?? (fighting ? "toll" : "idle");
                int seconds = Mathf.Max(0, Mathf.CeilToInt(pulseUntil - now));
                if (id != lastHint || (fighting && seconds != lastSecond))
                {
                    lastSecond = seconds;
                    if (fighting)
                        display.Say(
                            "Answer " + story.KeyName(story.CalledKey) + "   /   " + seconds + "s",
                            (3 - story.wounds) + " breaths left. " +
                                (focus != null ? "Trigger or E   /   " + Label(focus) : "Find the glowing seal."));
                    else if (focus != null)
                        display.Say(Label(focus), "Trigger or E to interact   •   A/X or J for your journal");
                    else
                        display.Hide();
                    lastHint = id;
                }
            }
            if (now >= cameraCheck)
            {
                cameraCheck = now + .2f;
                // The playable terrain is square, with the spawn 14 metres behind its centre.
                Vector3 centre = nodes["Spawn"].position + facing * Vector3.forward * 14, p = player.head.position - centre;
                if (Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.z)) > RoomRadius + .6f || p.y < -.5f)
                    player.Teleport(spawn, facing);
            }
        }
        Transform guide;
        readonly List<Vector3> flight = new List<Vector3>();
        Vector3 flightPosition;
        int flightLeg;
        Quaternion leftWingRest, rightWingRest;
        void PrepareGuide()
        {
            guide = new GameObject("Waywren").transform;
            guide.SetParent(set.transform, false);
            foreach (string part in new[] { "GuideBird", "GuideLeft", "GuideRight" })
                nodes[part].SetParent(guide, true);
            leftWingRest = nodes["GuideLeft"].localRotation;
            rightWingRest = nodes["GuideRight"].localRotation;
            guide.gameObject.SetActive(false);
        }
        Vector2 SurveyPosition(Vector3 position)
        {
            var origin = nodes["MapSW"].position;
            var east = nodes["MapSE"].position - origin;
            var north = nodes["MapNW"].position - origin;
            return new Vector2(Vector3.Dot(position-origin, east)/east.sqrMagnitude,
                               Vector3.Dot(position-origin, north)/north.sqrMagnitude);
        }
        void CallGuide()
        {
            var uv = SurveyPosition(player.head.position);
            int cell = Mathf.Clamp(Mathf.FloorToInt(uv.x*15),0,14) +
                       15*Mathf.Clamp(Mathf.FloorToInt(uv.y*15),0,14);
            var cells = story.works.GuideTrail(cell);
            if (cells.Count == 0) return;
            var origin = nodes["MapSW"].position;
            var east = nodes["MapSE"].position - origin;
            var north = nodes["MapNW"].position - origin;
            flight.Clear();
            foreach (int id in cells)
            {
                var point = origin + east*((id%15+.5f)/15) + north*((id/15+.5f)/15);
                point.y = story.works.Room.ground[id] + 1.66f;
                flight.Add(point);
            }
            flightLeg = 0;
            flightPosition = player.head.position + player.head.forward*.55f;
            guide.position = flightPosition;
            guide.gameObject.SetActive(true);
        }
        void FlyGuide()
        {
            if (!guide.gameObject.activeSelf) return;
            if (flightLeg < flight.Count)
            {
                var target = flight[flightLeg];
                var heading = target-flightPosition;
                heading.y = 0;
                if (heading.sqrMagnitude > .002f)
                    guide.rotation = Quaternion.LookRotation(heading);
                flightPosition = Vector3.MoveTowards(flightPosition,target,3.4f*Time.deltaTime);
                if ((flightPosition-target).sqrMagnitude < .0001f) flightLeg++;
            }
            guide.position = flightPosition + Vector3.up*(.05f*Mathf.Sin(Time.time*5));
            float wing = 28*Mathf.Sin(Time.time*18);
            nodes["GuideLeft"].localRotation = Quaternion.AngleAxis(wing,Vector3.forward)*leftWingRest;
            nodes["GuideRight"].localRotation = Quaternion.AngleAxis(-wing,Vector3.forward)*rightWingRest;
        }
        void ShowBook()
        {
            if (journalPage < 0)
            {
                display.Say("Witness book   /   " + story.LeafCount + " of 5 leaves   /   " + story.PlayTime(),
                            Objective + "   •   Trigger/E to turn a page. A/X or J to close.");
                if (InWorks && story.works.Room.early)
                {
                    display.Survey(paints[story.works.Room.key+"Survey"].mainTexture,
                                   SurveyPosition(player.head.position));
                }
            }
            else if (journalPage == 6)
                display.Say(worksPlan.logTitle,worksPlan.logEntry);
            else if (journalPage==5 && InWorks)
                display.Say("The fourth hand",story.works.Register());
            else
                display.Say(BellwakeJourney.Titles[journalPage], BellwakeJourney.Leaf(journalPage));
        }
        bool BearingClear()
        {
            Vector3 eye = player.head.position;
            Vector3 target = nodes[observation.sight].position - eye;
            Vector3 line = target.normalized;
            if (Vector3.Dot(player.head.forward,line) < .9984f) return false;
            if (!Physics.Raycast(eye+line*3.2f,line,out RaycastHit hit,target.magnitude-4.3f,
                                 player.surfaces,QueryTriggerInteraction.Ignore)) return true;
            Vector3 local = set.transform.InverseTransformPoint(hit.point);
            return hit.collider.name=="C_Solids" && Mathf.Max(Mathf.Abs(local.x),Mathf.Abs(local.z)) >= RoomRadius-.35f;
        }
        void FindFocus()
        {
            focus = null;
            if (observation != null)
            {
                if (Vector3.Distance(nodes[observation.id].position,player.head.position) <= 4.3f)
                {
                    focus = observation.id;
                    return;
                }
                observation = null;
            }
            float nearest = float.MaxValue;
            foreach (var pair in points)
            {
                Transform t = nodes[pair.Key];
                if (!t.gameObject.activeSelf)
                    continue;
                Vector3 delta = t.position - player.head.position;
                float distance = delta.magnitude;
                bool close = distance < 9;
                pair.Value.gameObject.SetActive(close);
                if (!close)
                    continue;
                display.Face(pair.Value);
                bool hand =
                    XRSettings.isDeviceActive && ((player.leftHand.position - t.position).sqrMagnitude < .8f ||
                                                  (player.rightHand.position - t.position).sqrMagnitude < .8f);
                float dot = Vector3.Dot(player.head.forward, delta / Mathf.Max(.01f, distance));
                if (!hand && (distance > 4.1f || dot < .64f))
                    continue;
                if (Physics.Raycast(player.head.position, delta.normalized, Mathf.Max(0, distance - .45f),
                                    player.surfaces, QueryTriggerInteraction.Ignore))
                    continue;
                bool readBySight = InPassage || story.ending != 0;
                float weight = hand && !readBySight ? 0 : readBySight ? distance*.025f + 20*(1-dot) : distance + 4*(1-dot);
                if (weight < nearest)
                {
                    nearest = weight;
                    focus = pair.Key;
                }
            }
        }
        void AnimateSet()
        {
            float t = Time.time;
            if(InWorks) { AnimateWorks(false); return; }
            if (InPassage && !string.IsNullOrEmpty(movingTrail))
            {
                float progress=(t-trailTime)/.09f;
                int leg=Mathf.FloorToInt(progress);
                if(leg<movingTrail.Length)
                {
                    Vector3 from=leg==0 ? trailStart : ChartPoint(movingTrail[leg-1]-65);
                    nodes["Pawn"].position=Vector3.Lerp(from,ChartPoint(movingTrail[leg]-65),progress-leg);
                }
                else { nodes["Pawn"].position=ChartPoint(Route.Piece.p); movingTrail=null; }
            }
            if (struck != null)
            {
                float age = t - strikeAt;
                float angle =
                    story.room == 2 ? 90 * Mathf.Clamp01(age * 2) : 18 * Mathf.Sin(age * 15) * Mathf.Exp(-age * 4);
                struck.rotation =
                    Quaternion.AngleAxis(angle, story.room == 2 ? Vector3.up : facing * Vector3.forward) *
                    strikeRest;
                if (age > 1.4f)
                    struck = null;
            }
            if (story.room == 4 && story.challenged && !story.Solved)
            {
                var wave = nodes["HushWave"];
                float phase = 1 - Mathf.Clamp01((pulseUntil - Time.unscaledTime) / 24);
                wave.localScale = waveScale * Mathf.Lerp(1, 13, phase);
            }
            if (nodes.TryGetValue("SpeakerHead", out var face))
            {
                Vector3 toPlayer = player.head.position - face.position;
                toPlayer.y = 0;
                Vector3 neutral = -(facing * Vector3.forward);
                float turn = toPlayer.sqrMagnitude < 72
                                 ? Mathf.Clamp(Vector3.SignedAngle(neutral, toPlayer, Vector3.up), -32, 32)
                                 : 0;
                face.rotation = Quaternion.Slerp(
                    face.rotation, Quaternion.AngleAxis(turn, Vector3.up) * rest[face.name], Time.deltaTime * 5);
                var arm = nodes["SpeakerArm"];
                float gesture =
                    Mathf.Clamp01(gestureUntil - t) * Mathf.Min(1, (3 - Mathf.Clamp(gestureUntil - t, 0, 3)) * 4);
                arm.rotation =
                    Quaternion.AngleAxis(2 * Mathf.Sin(t * 1.6f) + gesture * (16 + 5 * Mathf.Sin(t * 5)),
                                         facing * Vector3.right) *
                    rest[arm.name];
            }
            if (nodes.TryGetValue("Familiar", out var pet))
                pet.rotation = Quaternion.AngleAxis(8 * Mathf.Sin(t * .85f), Vector3.up) * rest["Familiar"];
            if (story.room == 4 && nodes.TryGetValue("GreatBell", out var bell))
                bell.rotation =
                    Quaternion.AngleAxis((story.challenged && !story.Solved ? 7 : 1) * Mathf.Sin(t * 1.8f),
                                         facing * Vector3.forward) *
                    rest["GreatBell"];
        }
        void Interact(string id)
        {
            string line;
            if(InWorks)
            {
                var station=story.works.Station(id);
                string title=station.label;
                if (id=="A_Book" && nodes.ContainsKey("Linnet") && story.works.Signal("landed")!=0 && voyageFraction<1)
                {
                    Say(title,"Her sail is rounding the last stone. Elin will have the book when she makes fast.");
                    return;
                }
                if (!string.IsNullOrEmpty(station.sight) && story.works.Signal("charter") != 0 &&
                    story.works.Signal(station.evidence) == 0)
                {
                    if (observation != station)
                    {
                        observation = station;
                        Say(title,station.direction,18);
                        return;
                    }
                    if (!BearingClear())
                    {
                        Say(title,"The mark is outside the sight. "+station.direction);
                        return;
                    }
                    observation = null;
                }
                line=story.works.Use(id,out string destination);
                if(!string.IsNullOrEmpty(destination))
                {
                    if(destination.StartsWith("#"))
                    {
                        spawn=Arrival(); player.Teleport(spawn,facing); Save(); Say(title,line); return;
                    }
                    if(destination=="@choir") story.works.active=false;
                    if(destination=="@final") { story.works.active=false;story.Gate(); }
                    StartCoroutine(EnterRoom());
                }
                else { notes.PlayOneShot(chimes[station.note]);Sync();Save();Say(title,line); }
                return;
            }
            if (InPassage)
            {
                if (id=="A_Gate" && Route.Done && story.Gate())
                {
                    Route.Leave();
                    if(story.room==1)
                    {
                        story.works.chamber=Array.FindIndex(worksPlan.rooms,r=>r.early);
                        story.works.camp="";
                        story.works.active=true;
                    }
                    StartCoroutine(EnterRoom());
                    return;
                }
                trailStart=nodes["Pawn"].position;
                line=Route.Use(id);
                movingTrail=Route.travel;
                trailTime=Time.time;
                if(id=="A_Talk") gestureUntil=Time.time+3;
                if(id.StartsWith("A_Key") || id=="A_Stamp") notes.PlayOneShot(chimes[Route.Piece.win?0:1]);
                Sync();Save();Say(Label(id),line);
                return;
            }
            switch (id)
            {
            case "A_RoadBook":
                var leaf = worksPlan.roadLeaves[roadPage];
                Say(leaf.name, (story.ending==1 ? leaf.shared : leaf.freed) + "   •   E / trigger for the next letter.", 12);
                roadPage=(roadPage+1)%worksPlan.roadLeaves.Length;
                return;
            case "A_Nameplate":
                line="NIGHT ROLL  /  Ina, fourth hand of the flood watch. Paid in full. Below the engraving hangs a left-handed pilot’s knot.";
                break;
            case "A_Ina":
            case "A_Roster":
                line = story.Epilogue();
                if (HasFloodBook) line += " " + worksPlan.logEndings[story.ending-1];
                if(story.works.Remembered(worksPlan,"named")) line+=" Below it hangs a new brass plate: Ina, fourth hand of the night shift.";

                break;
            case "A_Meadow":
                StartCoroutine(EnterMeadow());
                return;
            case "A_Talk":
                gestureUntil = Time.time + 3;
                bool was = story.challenged;
                line = story.Talk();
                if (!was)
                    pulseUntil = Time.unscaledTime + 32;
                break;
            case "A_Letter":
                line = story.ReadLetter();
                break;
            case "A_Gate":
                if (story.ending != 0)
                {
                    if (Time.unscaledTime < restartUntil)
                    {
                        story = new BellwakeJourney();
                        StartCoroutine(EnterRoom());
                        return;
                    }
                    restartUntil = Time.unscaledTime + 4;
                    line = "Use the arch again within four seconds to replace your completed journey.";
                    break;
                }
                if (story.room < atlas.regions.Length && Route.completed == story.room &&
                    story.commissioned && (story.room==0 || story.Solved))
                {
                    Route.active=true;
                    StartCoroutine(EnterRoom());
                    return;
                }
                if(story.room==3 && story.Solved)
                {
                    story.works.active=true;
                    story.works.chamber=0;story.works.camp="";
                    StartCoroutine(EnterRoom());
                    return;
                }
                if (story.Gate())
                {
                    StartCoroutine(EnterRoom());
                    return;
                }
                line = story.Objective();
                break;
            case "A_Lens":
                line = story.BeamCount == 4 ? "Molten amber sings in the casting cup."
                                            : "The casting cup is cold. Trace the light back to the kiln.";
                break;
            case "A_End0":
            case "A_End1":
                if (story.Choose(id == "A_End0" ? 1 : 2))
                {
                    notes.PlayOneShot(chimes[0]);
                    StartCoroutine(EnterRoom());
                    return;
                }
                line = story.Objective();
                break;
            default:
                int key = id[id.Length - 1] - '0';
                if (story.room == 1 || story.room == 2)
                {
                    if (struck != null && story.room == 1)
                        struck.rotation = strikeRest;
                    struck = nodes["Rotor" + key];
                    strikeRest = struck.rotation;
                    strikeAt = Time.time;
                }
                int wounds = story.wounds;
                line = story.Key(key);
                notes.PlayOneShot(
                    chimes[story.room == 4 && (story.wounds > wounds || !story.challenged) ? 3 : key]);
                if (story.room == 4)
                    pulseUntil = Time.unscaledTime + 24;
                break;
            }
            Sync();
            Save();
            Say(Label(id), line);
        }
        IEnumerator EnterMeadow()
        {
            loading = true;
            if (profiler != null)
                profiler.StartTravel();
            player.MovementLocked = true;
            try
            {
                yield return Fade(0, 1);
                display.Hide();
                lastHint = null;
                yield return ReleaseArea();
                RenderSettings.skybox = null;
                cam.clearFlags = CameraClearFlags.SolidColor;
                RenderSettings.fogColor = new Color(.66f, .78f, .75f);
                RenderSettings.fogStartDistance = 180;
                RenderSettings.fogEndDistance = MeadowTileWindow.Visible - 20;
                meadow = new GameObject("2048m rolling meadow");
                var terrain = meadow.AddComponent<MeadowWorld>();
                terrain.Initialize(player);
                village = gameObject.AddComponent<MossbellVillage>();
                village.Initialize(player, meadow);
                sign = Instantiate(Resources.Load<GameObject>(Path + "Rooms/TrailSign"), meadow.transform);
                sign.transform.position = new Vector3(0, MeadowWorld.Height(0, 3), 3);
                foreach (var r in sign.GetComponentsInChildren<MeshRenderer>())
                    Paint(r);
                outdoors = true;
                player.ResetPlayer();
                Physics.SyncTransforms();
                yield return Fade(1, 0);
                if (profiler != null) profiler.Begin("Long Meadow");
            }
            finally
            {
                loading = false;
                player.MovementLocked = false;
                curtainRenderer.enabled = false;
            }
        }
#if UNITY_EDITOR || DEVELOPMENT_BUILD
        [ContextMenu("Run Bellwake round-trip check (Play Mode)")]
        void CheckTravel()
        {
            if (Application.isPlaying && !loading && !outdoors && !checkingTravel)
                StartCoroutine(RoundTrips());
        }

        IEnumerator RoundTrips()
        {
            var previousStory = story;
            checkingTravel = true;
            try
            {
                for (int lap = 0; lap < 3; lap++)
                {
                    for (int r = 0; r < BellwakeJourney.Rooms.Length; r++)
                    {
                        story = new BellwakeJourney { room = r, commissioned = true, seals = Mathf.Max(0,r-1) };
                        yield return EnterRoom();
                        if (set == null || set.name != BellwakeJourney.Rooms[r] ||
                            meadow != null || village != null || paints.Count == 0 ||
                            !Physics.Raycast(spawn + Vector3.up, Vector3.down, 3, player.surfaces))
                            throw new InvalidOperationException("Round-trip room or floor missing at " + r);
                    }
                    for (int r=0;r<atlas.regions.Length;r++)
                    {
                        story=new BellwakeJourney {room=r,seals=r,commissioned=true,
                            passage=new BellwakePassage {active=true,completed=r}};
                        yield return EnterRoom();
                        if (!InPassage || set.name!=atlas.regions[r].key || Route.book==null ||
                            !Physics.Raycast(spawn+Vector3.up,Vector3.down,3,player.surfaces))
                            throw new InvalidOperationException("Passage missing on round trip: "+r);
                    }
                    for(int r=0;r<worksPlan.rooms.Length;r++)
                    {
                        story=new BellwakeJourney {room=worksPlan.rooms[r].early ? 1 : 3,seals=3,commissioned=true,
                            works=new BellwakeWorks {active=true,chamber=r}};
                        yield return EnterRoom();
                        if(!InWorks || set.name!=worksPlan.rooms[r].key ||
                            !Physics.Raycast(spawn+Vector3.up,Vector3.down,3,player.surfaces))
                            throw new InvalidOperationException("Lower Works room missing on round trip: "+r);
                    }
                    yield return EnterMeadow();
                    if (set != null || nodes.Count != 0 || score.clip != null || sky.GetTexture("_Panorama") != null)
                        throw new InvalidOperationException("A chapter still owns resources in the meadow.");
                    yield return village.CheckCrossing(true);
                    yield return village.CheckCrossing(false);
                }
                Debug.Log("Bellwake passed three laps of every chapter and three meadow/village round trips.");
            }
            finally
            {
                story = previousStory;
                checkingTravel = false;
                StartCoroutine(EnterRoom());
            }
        }
#endif
        void OnApplicationPause(bool paused)
        {
            if (paused && story != null && !loading) Save();
        }
        void OnApplicationQuit()
        {
            if (story != null && !loading) Save();
        }
        void OnDestroy()
        {
            if (set != null)
                Destroy(set);
            if (meadow != null) Destroy(meadow);
            if (village != null) Destroy(village);
            if (display != null) display.Dispose();
            foreach (var m in paints.Values)
                Destroy(m);
            if (curtain != null)
                Destroy(curtain);
            if (sky != null)
                Destroy(sky);
        }
    }
}
