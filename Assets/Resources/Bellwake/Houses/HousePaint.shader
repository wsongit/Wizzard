Shader "Wizzard/HousePaint" {
 Properties { _MainTex ("Paint",2D)="white"{} }
 SubShader { Tags {"RenderType"="Opaque"} Cull Off Pass {
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 struct Input {float4 vertex:POSITION;float2 uv:TEXCOORD0;fixed4 color:COLOR;UNITY_VERTEX_INPUT_INSTANCE_ID};
 struct Output {float4 pos:SV_POSITION;float2 uv:TEXCOORD0;fixed4 color:COLOR;UNITY_VERTEX_OUTPUT_STEREO};
 sampler2D _MainTex;
 Output vert(Input v){Output o;UNITY_SETUP_INSTANCE_ID(v);UNITY_INITIALIZE_OUTPUT(Output,o);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);o.pos=UnityObjectToClipPos(v.vertex);o.uv=v.uv;o.color=v.color;return o;}
 fixed4 frag(Output i):SV_Target {UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);return fixed4(tex2D(_MainTex,i.uv).rgb*i.color.rgb,1);}
 ENDCG
 } } }
