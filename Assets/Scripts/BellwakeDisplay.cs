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
        Transform survey,pin;
        Material surveyInk,pinInk;
        readonly Material panelMaterial, captionInk, worldInk;
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
            panel.GetComponent<Renderer>().sharedMaterial = panelMaterial;
            heading =
                Text(card, new Vector3(-.595f, .153f, -.006f), TextAnchor.UpperLeft, new Color(1, .81f, .42f));
            body =
                Text(card, new Vector3(-.595f, .068f, -.006f), TextAnchor.UpperLeft, new Color(.98f, .96f, .86f));
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
        public void ClearSurvey()
        {
            if (survey==null) return;
            survey.gameObject.SetActive(false);
            surveyInk.mainTexture=null;
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
        public void Say(string title, string text)
        {
            ClearSurvey();
            card.gameObject.SetActive(true);
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
            return label;
        }
        public void Face(TextMesh label)
        {
            var t = label.transform;
            var d = t.position - head.position;
            t.rotation = Quaternion.LookRotation(d.sqrMagnitude > .001f ? d : head.forward, Vector3.up);
            // World scale is independent of FBX axis and unit conversion.
            var p = t.parent.lossyScale;
            t.localScale = new Vector3(2 / Mathf.Max(.001f, Mathf.Abs(p.x)), 2 / Mathf.Max(.001f, Mathf.Abs(p.y)),
                                       2 / Mathf.Max(.001f, Mathf.Abs(p.z)));
        }
        public void Hide()
        {
            ClearSurvey();
            card.gameObject.SetActive(false);
        }
        public void Dispose()
        {
            Font.textureRebuilt -= RefreshAtlas;
            Object.Destroy(captionInk);
            Object.Destroy(worldInk);
            Object.Destroy(panelMaterial);
            if(surveyInk!=null) Object.Destroy(surveyInk);
            if(pinInk!=null) Object.Destroy(pinInk);
            Object.Destroy(card.gameObject);
        }
    }
}
