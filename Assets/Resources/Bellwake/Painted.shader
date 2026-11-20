Shader "Wizzard/BellwakePaint" {
 Properties { _MainTex ("Paint",2D)="white"{} _GroundBrush ("Ground brushwork",2D)="gray"{} _GroundProfile ("Ground material",Float)=2 _Glow ("Inner light",Range(0,1))=0 _Window ("Lamplit glass",Range(0,1))=0 }
 SubShader { Tags { "RenderType"="Opaque" } Cull Off
 Pass { Tags {"LightMode"="ForwardBase"} CGPROGRAM
 #pragma target 3.0
 #pragma multi_compile_local __ BELLWAKE_CUTOUT
 #pragma multi_compile_local __ BELLWAKE_PORTRAIT BELLWAKE_KILN BELLWAKE_SHOP_WINDOW BELLWAKE_GROUND
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_fog
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 #include "Lighting.cginc"
 #include "../../Shaders/BellwakeGroundPrint.cginc"
 #include "../../Shaders/BellwakeEyes.cginc"
 #include "../../Shaders/BellwakeKiln.cginc"
 #include "../../Shaders/BellwakeTone.cginc"
 #include "../../Shaders/BellwakeFilter.cginc"
 struct V { float4 vertex:POSITION;float3 normal:NORMAL;float2 uv:TEXCOORD0;UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct F { float4 pos:SV_POSITION;float2 uv:TEXCOORD0;half shade:TEXCOORD1; UNITY_FOG_COORDS(2)
 #if defined(BELLWAKE_GROUND)
 float2 groundUV:TEXCOORD3;
 #endif
 UNITY_VERTEX_OUTPUT_STEREO };
 sampler2D _MainTex; float4 _MainTex_ST, _MainTex_TexelSize; half _Glow, _Window;
 sampler2D _GroundBrush; half _GroundProfile;
 F vert(V v){F o;UNITY_SETUP_INSTANCE_ID(v);UNITY_INITIALIZE_OUTPUT(F,o);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
 o.pos=UnityObjectToClipPos(v.vertex);o.uv=TRANSFORM_TEX(v.uv,_MainTex);half3 n=normalize(UnityObjectToWorldNormal(v.normal));
 #if defined(BELLWAKE_GROUND)
 o.groundUV=BellwakeBrushUV(mul(unity_ObjectToWorld,v.vertex).xz);
 #endif
 #if defined(BELLWAKE_KILN)
 float2 oven=BellwakeKiln(float2(o.uv.x,1.0-o.uv.y),_Time.y);
 o.uv=float2(oven.x,1.0-oven.y);
 #endif
 o.shade=.60+.15*n.y+.34*saturate(dot(n,normalize(_WorldSpaceLightPos0.xyz)));
 UNITY_TRANSFER_FOG(o,o.pos);return o;}
 fixed4 frag(F i):SV_Target {UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
 float2 paintUV=i.uv;
 #if defined(BELLWAKE_PORTRAIT)
 float2 px=BellwakeEyes(float2(i.uv.x,1.0-i.uv.y)*512.0,_Time.y)/512.0;
 paintUV=float2(px.x,1.0-px.y);
 #endif
 fixed4 c=BellwakeTile(_MainTex,paintUV,_MainTex_TexelSize,ddx(i.uv),ddy(i.uv));
 #if defined(BELLWAKE_GROUND)
 c.rgb=BellwakeGroundPrint(c.rgb,tex2D(_GroundBrush,i.groundUV),_GroundProfile);
 #endif
 #if defined(BELLWAKE_CUTOUT)
 clip(c.a-.45);
 #endif
 #if defined(BELLWAKE_SHOP_WINDOW)
 half3 lamplit = c.rgb * half3(1.55, .99, .61);
 c.rgb=lerp(WizzardSurfaceLight(c.rgb,i.shade,0,0),lamplit,_BellwakeNight*.91);
 #else
 c.rgb=WizzardSurfaceLight(c.rgb,i.shade,_Glow,_Window);
 #endif
 UNITY_APPLY_FOG(i.fogCoord,c);return fixed4(c.rgb,1);}
 ENDCG } }
}
