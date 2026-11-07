Shader "Wizzard/RetroGrass"
{
 Properties { _MainTex ("Grass", 2D) = "white" {} }
 SubShader {
 Tags { "RenderType"="Opaque" }
 Pass {
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_fog
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 sampler2D _MainTex;
 struct appdata { float4 vertex:POSITION; float2 uv:TEXCOORD0; float3 normal:NORMAL; UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct v2f { float4 vertex:SV_POSITION; float2 uv:TEXCOORD0; float shade:TEXCOORD1; UNITY_FOG_COORDS(2) UNITY_VERTEX_OUTPUT_STEREO };
 v2f vert(appdata v) {
 v2f o; UNITY_SETUP_INSTANCE_ID(v); UNITY_INITIALIZE_OUTPUT(v2f,o); UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
 o.vertex=UnityObjectToClipPos(v.vertex); o.uv=v.uv;
 o.shade=.72+.28*saturate(dot(UnityObjectToWorldNormal(v.normal),normalize(float3(.4,1,.3))));
 UNITY_TRANSFER_FOG(o,o.vertex); return o;
 }
 fixed4 frag(v2f i):SV_Target { fixed4 c=tex2D(_MainTex,i.uv)*i.shade; c.a=1; UNITY_APPLY_FOG(i.fogCoord,c); return c; }
 ENDCG
 }
 }
}
