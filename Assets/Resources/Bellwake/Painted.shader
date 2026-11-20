Shader "Wizzard/BellwakePaint" {
 Properties { _MainTex ("Paint",2D)="white"{} _Glow ("Inner light",Range(0,1))=0 _Window ("Lamplit glass",Range(0,1))=0 }
 SubShader { Tags { "RenderType"="Opaque" } Cull Off
 Pass { Tags {"LightMode"="ForwardBase"} CGPROGRAM
 #pragma target 3.0
 #pragma multi_compile_local __ BELLWAKE_CUTOUT
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_fog
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 #include "Lighting.cginc"
 #include "../../Shaders/BellwakeTone.cginc"
 #include "../../Shaders/BellwakeFilter.cginc"
 struct V { float4 vertex:POSITION;float3 normal:NORMAL;float2 uv:TEXCOORD0;UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct F { float4 pos:SV_POSITION;float2 uv:TEXCOORD0;half shade:TEXCOORD1; UNITY_FOG_COORDS(2) UNITY_VERTEX_OUTPUT_STEREO };
 sampler2D _MainTex; float4 _MainTex_ST, _MainTex_TexelSize; half _Glow, _Window;
 F vert(V v){F o;UNITY_SETUP_INSTANCE_ID(v);UNITY_INITIALIZE_OUTPUT(F,o);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
 o.pos=UnityObjectToClipPos(v.vertex);o.uv=TRANSFORM_TEX(v.uv,_MainTex);half3 n=normalize(UnityObjectToWorldNormal(v.normal));
 o.shade=.60+.15*n.y+.34*saturate(dot(n,normalize(_WorldSpaceLightPos0.xyz)));
 UNITY_TRANSFER_FOG(o,o.pos);return o;}
 fixed4 frag(F i):SV_Target {UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
 fixed4 c=BellwakeTile(_MainTex,i.uv,_MainTex_TexelSize,ddx(i.uv),ddy(i.uv));
 #if defined(BELLWAKE_CUTOUT)
 clip(c.a-.45);
 #endif
 c.rgb=WizzardSurfaceLight(c.rgb,i.shade,_Glow,_Window);UNITY_APPLY_FOG(i.fogCoord,c);return fixed4(c.rgb,1);}
 ENDCG } }
}
