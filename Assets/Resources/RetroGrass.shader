Shader "Wizzard/RetroGrass"
{
 Properties { _ShadeStrength ("Directional shading", Range(0,1)) = 0.35 _Color ("Tint", Color) = (1,1,1,1) _MainTex ("Low resolution surface", 2D) = "white" {} _TileScale ("Texture repeats per unit", Float) = 1 }
 SubShader {
 Tags { "RenderType"="Opaque" }
 Pass {
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_fog
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 sampler2D _MainTex; float _TileScale; float _ShadeStrength; fixed4 _Color;
 struct appdata { float4 vertex:POSITION; float3 normal:NORMAL; UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct v2f { float4 vertex:SV_POSITION; float3 pos:TEXCOORD0; float3 normal:TEXCOORD1; UNITY_FOG_COORDS(2) UNITY_VERTEX_OUTPUT_STEREO };
 v2f vert(appdata v) {
 v2f o; UNITY_SETUP_INSTANCE_ID(v); UNITY_INITIALIZE_OUTPUT(v2f,o); UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
 o.vertex=UnityObjectToClipPos(v.vertex); o.pos=v.vertex.xyz*_TileScale; o.normal=v.normal;
 UNITY_TRANSFER_FOG(o,o.vertex); return o;
 }
 fixed4 frag(v2f i):SV_Target {
 float3 weights=pow(abs(normalize(i.normal)),4); weights/=max(dot(weights,float3(1,1,1)),.0001);
 fixed4 c=tex2D(_MainTex,i.pos.zy)*weights.x+tex2D(_MainTex,i.pos.xz)*weights.y+tex2D(_MainTex,i.pos.xy)*weights.z;
 c.rgb*=_Color.rgb;
 c.rgb*=(1-_ShadeStrength)+_ShadeStrength*saturate(dot(normalize(i.normal),normalize(float3(.4,1,.3))));
 c.a=1; UNITY_APPLY_FOG(i.fogCoord,c); return c;
 }
 ENDCG
 }
 }
}
