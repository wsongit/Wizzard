Shader "Wizzard/VillageSurface"
{
 Properties { _CastShadows ("Cast shadows", Float) = 1 _MainTex ("Painted 64px tile", 2D) = "white" {} }
 SubShader {
 Tags { "RenderType"="Opaque" }
 Pass {
 Tags { "LightMode"="ForwardBase" }
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_fwdbase nolightmap nodirlightmap nodynlightmap novertexlight
 #pragma multi_compile_fog
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 #include "Lighting.cginc"
 #include "AutoLight.cginc"
 sampler2D _MainTex;
 struct appdata { float4 vertex:POSITION; float3 normal:NORMAL; float2 uv:TEXCOORD0; UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct v2f { float4 pos:SV_POSITION; float2 uv:TEXCOORD0; float3 normal:TEXCOORD1; float3 worldPos:TEXCOORD2; SHADOW_COORDS(3) UNITY_FOG_COORDS(4) UNITY_VERTEX_OUTPUT_STEREO };
 v2f vert(appdata v) {
  v2f o; UNITY_SETUP_INSTANCE_ID(v); UNITY_INITIALIZE_OUTPUT(v2f,o); UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
  o.pos=UnityObjectToClipPos(v.vertex);o.uv=v.uv;o.normal=UnityObjectToWorldNormal(v.normal);o.worldPos=mul(unity_ObjectToWorld,v.vertex).xyz;
  TRANSFER_SHADOW(o);UNITY_TRANSFER_FOG(o,o.pos);return o;
 }
 fixed4 frag(v2f i):SV_Target {
  UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
  fixed4 c=tex2D(_MainTex,i.uv);
  UNITY_LIGHT_ATTENUATION(atten,i,i.worldPos);
  float diffuse=saturate(dot(normalize(i.normal),normalize(_WorldSpaceLightPos0.xyz)));
  c.rgb*=float3(.57,.56,.53)+diffuse*atten*float3(.47,.45,.41);
  c.a=1;UNITY_APPLY_FOG(i.fogCoord,c);return c;
 }
 ENDCG
 }
 Pass {
 Tags { "LightMode"="ShadowCaster" }
 ZWrite On ZTest LEqual
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_shadowcaster
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 struct v2f { V2F_SHADOW_CASTER; UNITY_VERTEX_OUTPUT_STEREO };
 v2f vert(appdata_base v) {
  v2f o;UNITY_SETUP_INSTANCE_ID(v);UNITY_INITIALIZE_OUTPUT(v2f,o);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
  TRANSFER_SHADOW_CASTER_NORMALOFFSET(o);return o;
 }
 float _CastShadows;
 float4 frag(v2f i):SV_Target { clip(_CastShadows-.5);SHADOW_CASTER_FRAGMENT(i) }
 ENDCG
 }
 }
}
