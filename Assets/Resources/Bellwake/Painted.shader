Shader "Wizzard/BellwakePaint" {
 Properties { _MainTex ("Paint",2D)="white"{} _Glow ("Inner light",Range(0,1))=0 }
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
 struct V { float4 vertex:POSITION;float3 normal:NORMAL;float2 uv:TEXCOORD0;UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct F { float4 pos:SV_POSITION;float2 uv:TEXCOORD0;half shade:TEXCOORD1; UNITY_FOG_COORDS(2) UNITY_VERTEX_OUTPUT_STEREO };
 sampler2D _MainTex; float4 _MainTex_ST, _MainTex_TexelSize; half _Glow;
 F vert(V v){F o;UNITY_SETUP_INSTANCE_ID(v);UNITY_INITIALIZE_OUTPUT(F,o);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
 o.pos=UnityObjectToClipPos(v.vertex);o.uv=TRANSFORM_TEX(v.uv,_MainTex);half3 n=normalize(UnityObjectToWorldNormal(v.normal));
 o.shade=.60+.15*n.y+.34*saturate(dot(n,normalize(_WorldSpaceLightPos0.xyz)));
 UNITY_TRANSFER_FOG(o,o.pos);return o;}
 fixed4 frag(F i):SV_Target {UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
 // In magnification the RDP interpolated one triangle of a four-texel square.
 // Minified details use the ordinary mip chain to stay stable while the headset turns.
 float2 texel = i.uv * _MainTex_TexelSize.zw - .5;
 float footprint = max(length(ddx(texel)),length(ddy(texel)));
 fixed4 c = tex2D(_MainTex,i.uv);
 UNITY_BRANCH if (footprint < 1.0) {
     float2 base = floor(texel);
     float2 f = frac(texel);
     bool upper = f.x + f.y > 1.0;
     float2 corner = upper ? float2(1,1) : float2(0,0);
     float2 weights = upper ? 1.0-f : f;
     float stepDir = upper ? -1.0 : 1.0;
     float2 uv = (base+corner+.5)*_MainTex_TexelSize.xy;
     fixed4 centre = tex2Dlod(_MainTex,float4(uv,0,0));
     fixed4 right = tex2Dlod(_MainTex,float4(uv+float2(stepDir*_MainTex_TexelSize.x,0),0,0));
     fixed4 above = tex2Dlod(_MainTex,float4(uv+float2(0,stepDir*_MainTex_TexelSize.y),0,0));
     c = lerp(centre+(right-centre)*weights.x+(above-centre)*weights.y,c,smoothstep(.65,1.0,footprint));
 }
 #if defined(BELLWAKE_CUTOUT)
 clip(c.a-.45);
 #endif
 c.rgb*=lerp(i.shade,1.32,_Glow);UNITY_APPLY_FOG(i.fogCoord,c);return fixed4(c.rgb,1);}
 ENDCG } }
}
