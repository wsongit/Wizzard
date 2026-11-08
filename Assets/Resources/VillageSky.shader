Shader "Wizzard/VillageSky" {
 SubShader { Tags { "Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox" } Cull Off ZWrite Off
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 struct appdata { float4 vertex:POSITION; UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct v2f { float4 pos:SV_POSITION; float3 dir:TEXCOORD0; UNITY_VERTEX_OUTPUT_STEREO };
 v2f vert(appdata v) { v2f o; UNITY_SETUP_INSTANCE_ID(v); UNITY_INITIALIZE_OUTPUT(v2f,o); UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o); o.pos=UnityObjectToClipPos(v.vertex);o.dir=v.vertex.xyz;return o; }
 float hash(float2 p) { return frac(sin(dot(p,float2(127.1,311.7)))*43758.5453); }
 float noise(float2 p) { float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(hash(i),hash(i+float2(1,0)),f.x),lerp(hash(i+float2(0,1)),hash(i+1),f.x),f.y); }
 fixed4 frag(v2f i):SV_Target {
 float3 d=normalize(i.dir);float horizon=pow(1-saturate(d.y),3);
 float3 col=lerp(float3(.22,.32,.83),float3(.66,.70,.85),horizon);
 float2 uv=d.xz/max(.16,d.y)*2;
 float n=noise(uv)*.55+noise(uv*2.1)*.3+noise(uv*4.2)*.15;
 float cloud=smoothstep(.48,.75,n)*smoothstep(.01,.2,d.y);
 return fixed4(lerp(col,float3(.85,.87,.94),cloud*.85),1);
 }
 ENDCG }
 }
}
