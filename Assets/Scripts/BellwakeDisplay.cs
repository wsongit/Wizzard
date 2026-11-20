using System.Text;
using UnityEngine;

namespace Wizzard
{
    // A stereo-readable caption card. Geometry sits below the line of sight, with
    // a stationary world label on each station. No camera motion is driven by UI.
    public sealed class BellwakeDisplay
    {
        readonly Transform head, card;
        readonly TextMesh heading, body;
        readonly Font font;
        Transform survey,pin,advance;
        Material advanceInk,stampInk;
        Transform stamp,place;
        TextMesh placeName,placeShadow;
        float arrived;
        Material surveyInk,pinInk;
        readonly System.Collections.Generic.List<Transform> bearings = new System.Collections.Generic.List<Transform>();
        int usedBearings;
        static Vector2 MapPoint(Vector2 p) => new Vector2((16+480*p.x)/768f-.5f, .5f-(512-480*p.y)/544f);
        public void AddBearing(Vector2 from, Vector2 source, string voice)
        {
            if (usedBearings == bearings.Count)
            {
                var obj = GameObject.CreatePrimitive(PrimitiveType.Quad);
                Object.Destroy(obj.GetComponent<Collider>());
                obj.transform.SetParent(survey, false);
                obj.GetComponent<Renderer>().sharedMaterial = new Material(panelMaterial) { renderQueue = 3901 };
                bearings.Add(obj.transform);
            }
            var line = bearings[usedBearings++];
            Vector2 a = MapPoint(from), b = MapPoint(source+(source-from)*.15f), d = b-a;
            line.localPosition = new Vector3((a.x+b.x)*.5f, (a.y+b.y)*.5f, -.003f);
            line.localRotation = Quaternion.Euler(0,0,Mathf.Atan2(d.y,d.x)*Mathf.Rad2Deg);
            line.localScale = new Vector3(d.magnitude,.0045f,1);
            line.GetComponent<Renderer>().sharedMaterial.color = voice=="RainWoodCall" ? new Color(.20f,.36f,.48f)
                : voice=="RootWoodCall" ? new Color(.46f,.28f,.18f) : new Color(.61f,.22f,.19f);
            line.gameObject.SetActive(true);
        }
        readonly Material panelMaterial, frameMaterial, captionInk, worldInk;
        string revealText;
        int revealed;
        float revealStart;
        public bool Typing => revealText != null;
        public BellwakeDisplay(Transform head)
        {
            this.head = head;
            font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            var shader = Shader.Find("Wizzard/BellwakeLettering");
            worldInk = new Material(shader) { mainTexture = font.material.mainTexture };
            captionInk = new Material(worldInk) { renderQueue = 3901 };
            captionInk.SetFloat("_Depth", 8);
            Font.textureRebuilt += RefreshAtlas;
            card = new GameObject("Bellwake captions").transform;
            card.SetParent(head, false);
            card.localPosition = new Vector3(0, -.39f, 1.65f);
            var panel = GameObject.CreatePrimitive(PrimitiveType.Quad);
            Object.Destroy(panel.GetComponent<Collider>());
            panel.transform.SetParent(card, false);
            panel.transform.localScale = new Vector3(1.28f, .36f, 1);
            panelMaterial =
                new Material(shader) { color = new Color(.043f, .086f, .09f, .96f), renderQueue = 3900 };
            panelMaterial.SetFloat("_Depth", 8);
            frameMaterial = new Material(panelMaterial) {
                color = Color.white, mainTexture = Resources.Load<Texture2D>("Bellwake/Textures/Letterpress")
            };
            frameMaterial.SetFloat("_FullColor", 1);
            panel.GetComponent<Renderer>().sharedMaterial = frameMaterial;
            heading =
                Text(card, new Vector3(-.595f, .153f, -.006f), TextAnchor.UpperLeft, new Color(1, .81f, .42f));
            body =
                Text(card, new Vector3(-.595f, .068f, -.006f), TextAnchor.UpperLeft, new Color(.98f, .96f, .86f));
        }
        public void SetQueue(int queue)
        {
            frameMaterial.renderQueue = queue;
            captionInk.renderQueue = queue + 1;
            if (surveyInk!=null) surveyInk.renderQueue=queue;
        }
        void RefreshAtlas(Font changed)
        {
            if (changed != font)
                return;
            worldInk.mainTexture = captionInk.mainTexture = font.material.mainTexture;
        }
        TextMesh Text(Transform parent, Vector3 pos, TextAnchor anchor, Color color)
        {
            var label = new GameObject("Lettering").AddComponent<TextMesh>();
            label.transform.SetParent(parent, false);
            label.transform.localPosition = pos;
            label.font = font;
            label.fontSize = 64;
            label.characterSize = .01f;
            label.anchor = anchor;
            label.color = color;
            label.lineSpacing = .95f;
            label.GetComponent<Renderer>().sharedMaterial = parent == card ? captionInk : worldInk;
            return label;
        }
        static string Wrap(string value, int columns)
        {
            var result = new StringBuilder(value.Length + 8);
            int line = 0;
            foreach (var word in value.Split(' '))
            {
                if (line > 0 && line + 1 + word.Length > columns)
                {
                    result.Append('\n');
                    line = 0;
                }
                if (line > 0)
                {
                    result.Append(' ');
                    line++;
                }
                result.Append(word);
                line += word.Length;
            }
            return result.ToString();
        }
        static void Fit(TextMesh label, float width, float height, float maxScale)
        {
            var bounds = label.GetComponent<Renderer>().localBounds.size;
            float s = Mathf.Min(
                maxScale, Mathf.Min(width / Mathf.Max(.001f, bounds.x), height / Mathf.Max(.001f, bounds.y)));
            label.transform.localScale = Vector3.one * s;
        }
        public void Arrival(string name)
        {
            if(place==null)
            {
                place=new GameObject("District title").transform;
                place.SetParent(head,false);
                place.localPosition=new Vector3(0,.17f,2);
                placeName=Text(place,Vector3.zero,TextAnchor.MiddleCenter,Color.white);
                placeShadow=Text(place,new Vector3(.008f,-.009f,.001f),TextAnchor.MiddleCenter,Color.black);
                placeName.GetComponent<Renderer>().sharedMaterial=captionInk;
                placeShadow.GetComponent<Renderer>().sharedMaterial=captionInk;
                placeName.fontStyle=placeShadow.fontStyle=FontStyle.Italic;
            }
            placeName.text=placeShadow.text=name;
            Fit(placeName,1.32f,.13f,2.0f);
            placeShadow.transform.localScale=placeName.transform.localScale;
            arrived=Time.unscaledTime;
            place.gameObject.SetActive(true);
            TickArrival(true);
        }
        public void TickArrival(bool clear)
        {
            if(place==null || !place.gameObject.activeSelf)return;
            float t=Time.unscaledTime-arrived;
            if(!clear || t>=2.45f){place.gameObject.SetActive(false);return;}
            float alpha=Mathf.SmoothStep(0,1,Mathf.Min(t/.20f,(2.45f-t)/.65f));
            placeName.color=new Color(1,.91f,.73f,alpha);
            placeShadow.color=new Color(.10f,.09f,.10f,.85f*alpha);
        }
        void ClearStamp()
        {
            if(stamp==null || !stamp.gameObject.activeSelf)return;
            stamp.gameObject.SetActive(false);
            body.transform.localPosition=new Vector3(-.595f,.068f,-.006f);
        }
        public void StampPurchase(int item)
        {
            if(stamp==null)
            {
                var obj=GameObject.CreatePrimitive(PrimitiveType.Quad);
                Object.Destroy(obj.GetComponent<Collider>());
                stamp=obj.transform;stamp.SetParent(card,false);
                stamp.localPosition=new Vector3(-.486f,-.036f,-.006f);
                stamp.localScale=Vector3.one*.21f;
                stampInk=new Material(frameMaterial){mainTexture=Resources.Load<Texture2D>("Bellwake/Textures/ProvisionStamps"),
                    mainTextureScale=new Vector2(.25f,1),renderQueue=3902};
                obj.GetComponent<Renderer>().sharedMaterial=stampInk;
            }
            stampInk.mainTextureOffset=new Vector2(item*.25f,0);
            body.transform.localPosition=new Vector3(-.35f,.060f,-.006f);
            Fit(body,.93f,.20f,.83f);
            stamp.gameObject.SetActive(true);
        }
        public void ClearSurvey()
        {
            if (survey==null) return;
            survey.gameObject.SetActive(false);
            surveyInk.mainTexture=null;
            foreach (var line in bearings) line.gameObject.SetActive(false);
            usedBearings=0;
        }
        public void Survey(Texture image, Vector2? position = null)
        {
            if (survey==null)
            {
                var sheet=GameObject.CreatePrimitive(PrimitiveType.Quad);
                Object.Destroy(sheet.GetComponent<Collider>());
                survey=sheet.transform;survey.SetParent(card,false);
                survey.localPosition=new Vector3(0,.56f,0);survey.localScale=new Vector3(1.08f,.765f,1);
                surveyInk=new Material(panelMaterial){color=Color.white,renderQueue=3900};
                surveyInk.SetFloat("_FullColor",1);
                sheet.GetComponent<Renderer>().sharedMaterial=surveyInk;
                var marker=GameObject.CreatePrimitive(PrimitiveType.Quad);
                Object.Destroy(marker.GetComponent<Collider>());pin=marker.transform;pin.SetParent(survey,false);
                pin.localScale=new Vector3(.021f,.030f,1);
                pinInk=new Material(panelMaterial){color=new Color(.83f,.16f,.08f),renderQueue=3901};
                marker.GetComponent<Renderer>().sharedMaterial=pinInk;
            }
            surveyInk.mainTexture=image;
            pin.gameObject.SetActive(position.HasValue);
            if (position.HasValue)
            {
                Vector2 p = position.Value;
                pin.localPosition = new Vector3((16 + 480*p.x)/768f - .5f, .5f - (512 - 480*p.y)/544f, -.006f);
            }
            survey.gameObject.SetActive(true);
        }
        public void BeginDialogue(string title, string text)
        {
            Say(title, text);
            if(advance==null)
            {
                var cue=GameObject.CreatePrimitive(PrimitiveType.Quad);
                Object.Destroy(cue.GetComponent<Collider>());
                advance=cue.transform;advance.SetParent(card,false);
                advance.localPosition=new Vector3(.584f,-.125f,-.008f);
                advance.localScale=Vector3.one*.042f;
                advanceInk=new Material(frameMaterial){mainTexture=Resources.Load<Texture2D>("Bellwake/Textures/PocketGlyphs"),
                    mainTextureScale=new Vector2(1f/16,1),mainTextureOffset=new Vector2(13f/16,0),renderQueue=3902};
                cue.GetComponent<Renderer>().sharedMaterial=advanceInk;
                cue.SetActive(false);
            }
            revealText = body.text;
            revealed = 0;
            revealStart = Time.unscaledTime;
            body.text = "";
        }
        public void TickDialogue(float lettersPerSecond)
        {
            if (!Typing) return;
            int count = Mathf.Min(revealText.Length, 1 + (int)((Time.unscaledTime-revealStart)*lettersPerSecond));
            if (count == revealText.Length) FinishDialogue();
            else if (count != revealed)
            {
                revealed = count;
                body.text = revealText.Substring(0,count);
            }
        }
        public void FinishDialogue()
        {
            if (Typing)
            {
                body.text = revealText;
                advance.gameObject.SetActive(true);
            }
            revealText = null;
        }
        public void Say(string title, string text)
        {
            ClearSurvey();
            ClearStamp();
            if(advance!=null)advance.gameObject.SetActive(false);
            card.gameObject.SetActive(true);
            revealText = null;
            heading.text = title.ToUpperInvariant();
            body.text = Wrap(text, 51);
            Fit(heading, 1.18f, .068f, .84f);
            Fit(body, 1.18f, .215f, .83f);
        }
        public TextMesh Label(Transform point, string value)
        {
            var label = Text(point, Vector3.up * .55f, TextAnchor.LowerCenter, new Color(1, .89f, .63f));
            label.transform.position = point.position + Vector3.up * .48f;
            label.text = value;
            // World scale is independent of FBX axis and unit conversion.
            var p = point.lossyScale;
            label.transform.localScale = new Vector3(2 / Mathf.Max(.001f, Mathf.Abs(p.x)), 2 / Mathf.Max(.001f, Mathf.Abs(p.y)),
                                       2 / Mathf.Max(.001f, Mathf.Abs(p.z)));
            label.gameObject.SetActive(false);
            return label;
        }
        public void Face(TextMesh label)
        {
            var t = label.transform;
            var d = t.position - head.position;
            t.rotation = Quaternion.LookRotation(d.sqrMagnitude > .001f ? d : head.forward, Vector3.up);
        }
        public void Hide()
        {
            ClearSurvey();
            revealText = null;
            card.gameObject.SetActive(false);
        }
        public void Dispose()
        {
            Font.textureRebuilt -= RefreshAtlas;
            Object.Destroy(captionInk);
            Object.Destroy(worldInk);
            Object.Destroy(panelMaterial);
            Object.Destroy(frameMaterial);
            if(advanceInk!=null)Object.Destroy(advanceInk);
            if(stampInk!=null)Object.Destroy(stampInk);
            if(place!=null)Object.Destroy(place.gameObject);
            if(surveyInk!=null) Object.Destroy(surveyInk);
            foreach (var line in bearings) Object.Destroy(line.GetComponent<Renderer>().sharedMaterial);
            if(pinInk!=null) Object.Destroy(pinInk);
            Object.Destroy(card.gameObject);
        }
    }
}
