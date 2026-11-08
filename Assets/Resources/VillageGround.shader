Shader "Wizzard/VillageGround"
{
 Properties {
  _MainTex ("Painted 64px grass tile", 2D) = "white" {}
  _DirtTex ("Painted 64px dirt tile", 2D) = "white" {}
  _PathMask ("Village path coverage", 2D) = "black" {}
  _MaskTransform ("Mask UV scale and offset", Vector) = (0.034782609,0.035087719,0.478260870,0.403508772)
 }
 SubShader {
 Tags { "RenderType"="Opaque" "Queue"="Geometry" }
 ZWrite On ZTest LEqual Cull Back
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
 sampler2D _MainTex, _DirtTex, _PathMask;
 float4 _MaskTransform;
 struct appdata { float4 vertex:POSITION; float3 normal:NORMAL; float2 uv:TEXCOORD0; UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct v2f { float4 pos:SV_POSITION; float2 uv:TEXCOORD0; float3 normal:TEXCOORD1; float3 worldPos:TEXCOORD2; SHADOW_COORDS(3) UNITY_FOG_COORDS(4) UNITY_VERTEX_OUTPUT_STEREO };
 v2f vert(appdata v) {
  v2f o; UNITY_SETUP_INSTANCE_ID(v); UNITY_INITIALIZE_OUTPUT(v2f,o); UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
  o.pos=UnityObjectToClipPos(v.vertex);o.uv=v.uv;o.normal=UnityObjectToWorldNormal(v.normal);o.worldPos=mul(unity_ObjectToWorld,v.vertex).xyz;
  TRANSFER_SHADOW(o);UNITY_TRANSFER_FOG(o,o.pos);return o;
 }
 fixed4 frag(v2f i):SV_Target {
  UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
  // Authored UVs are Blender ground coordinates / 4. Both tiles share them,
  // so junctions blend on one solid surface without overlapping road meshes.
  float2 maskUV=i.uv*_MaskTransform.xy+_MaskTransform.zw;
  fixed coverage=tex2D(_PathMask,maskUV).r;
  fixed3 grass=tex2D(_MainTex,i.uv).rgb;
  fixed3 dirt=tex2D(_DirtTex,i.uv).rgb;
  fixed4 c=fixed4(lerp(grass,dirt,coverage),1);
  UNITY_LIGHT_ATTENUATION(atten,i,i.worldPos);
  float diffuse=saturate(dot(normalize(i.normal),normalize(_WorldSpaceLightPos0.xyz)));
  c.rgb*=float3(.57,.56,.53)+diffuse*atten*float3(.47,.45,.41);
  UNITY_APPLY_FOG(i.fogCoord,c);return c;
 }
 ENDCG
 }
 Pass {
 Tags { "LightMode"="ShadowCaster" }
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
 float4 frag(v2f i):SV_Target { SHADOW_CASTER_FRAGMENT(i) }
 ENDCG
 }
 }
}
