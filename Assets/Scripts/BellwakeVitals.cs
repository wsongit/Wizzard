using UnityEngine;

namespace Wizzard
{
    // Hearts and marks share one small mesh and a pixel atlas. Only a changed value rewrites its UVs.
    public sealed class BellwakeVitals
    {
        const int MaxDigits=10, MaxGlyphs=4+MaxDigits;
        readonly Mesh mesh;
        readonly MeshRenderer renderer;
        readonly Material ink;
        readonly Vector2[] uv=new Vector2[MaxGlyphs*4];
        readonly int[] triangles=new int[MaxGlyphs*6];
        int hearts=-1, marks=-1;

        public BellwakeVitals(Transform head)
        {
            var panel=new GameObject("Hearts and ferry marks");
            panel.transform.SetParent(head,false);
            panel.transform.localPosition=new Vector3(-.64f,.39f,1.65f);
            var vertices=new Vector3[MaxGlyphs*4];
            var tint=new Color32[vertices.Length];
            for(int i=0;i<MaxGlyphs;i++)
            {
                float left=i<3 ? i*.070f : i==3 ? 0 : .054f+(i-4)*.034f;
                float top=i<3 ? 0 : -.078f;
                float size=i<3 ? .069f : .059f;
                int k=4*i;
                vertices[k]=new Vector3(left,top,0);
                vertices[k+1]=new Vector3(left+size,top,0);
                vertices[k+2]=new Vector3(left+size,top-size,0);
                vertices[k+3]=new Vector3(left,top-size,0);
                for(int v=k;v<k+4;v++)tint[v]=Color.white;
                int t=6*i;
                triangles[t]=k;triangles[t+1]=k+1;triangles[t+2]=k+2;
                triangles[t+3]=k;triangles[t+4]=k+2;triangles[t+5]=k+3;
            }
            mesh=new Mesh { name="Pocket glyph strip",vertices=vertices,colors32=tint };
            mesh.MarkDynamic();
            panel.AddComponent<MeshFilter>().sharedMesh=mesh;
            renderer=panel.AddComponent<MeshRenderer>();
            ink=new Material(Shader.Find("Wizzard/BellwakeLettering")){
                mainTexture=Resources.Load<Texture2D>("Bellwake/Textures/PocketGlyphs"),renderQueue=3760
            };
            ink.SetFloat("_FullColor",1);
            ink.SetFloat("_Depth",8);
            renderer.sharedMaterial=ink;
            renderer.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows=false;
            renderer.enabled=false;
        }
        void Stamp(int slot,int glyph)
        {
            int k=4*slot;
            float l=glyph/16f, r=(glyph+1)/16f;
            uv[k]=new Vector2(l,1); uv[k+1]=new Vector2(r,1);
            uv[k+2]=new Vector2(r,0); uv[k+3]=new Vector2(l,0);
        }
        public void Show(bool visible,int currentHearts,int currentMarks)
        {
            if(renderer.enabled!=visible)renderer.enabled=visible;
            if(!visible || (hearts==currentHearts && marks==currentMarks))return;
            hearts=currentHearts;marks=currentMarks;
            for(int i=0;i<3;i++)Stamp(i,i<hearts?0:1);
            Stamp(3,2);
            string count=Mathf.Max(0,marks).ToString(System.Globalization.CultureInfo.InvariantCulture);
            for(int i=0;i<count.Length;i++)Stamp(4+i,3+count[i]-'0');
            mesh.uv=uv;
            mesh.SetTriangles(triangles,0,(4+count.Length)*6,0);
        }
        public void Dispose()
        {
            Object.Destroy(renderer.gameObject);Object.Destroy(mesh);Object.Destroy(ink);
        }
    }
}
