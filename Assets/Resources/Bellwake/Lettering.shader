Shader "Wizzard/BellwakeLettering" {
 Properties { _MainTex ("Font atlas",2D)="white"{} _Color ("Tint", Color)=(1,1,1,1) _Depth ("Depth test",Float)=4 }
 SubShader { Tags { "Queue"="Transparent" "RenderType"="Transparent" }
 Cull Off ZWrite Off ZTest [_Depth] Blend SrcAlpha OneMinusSrcAlpha
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 struct V {float4 vertex:POSITION;float4 color:COLOR;float2 uv:TEXCOORD0;UNITY_VERTEX_INPUT_INSTANCE_ID};
 struct F {float4 pos:SV_POSITION;fixed4 color:COLOR;float2 uv:TEXCOORD0;UNITY_VERTEX_OUTPUT_STEREO};
 fixed4 _Color;sampler2D _MainTex;
 F vert(V v){F o;UNITY_SETUP_INSTANCE_ID(v);UNITY_INITIALIZE_OUTPUT(F,o);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
 o.pos=UnityObjectToClipPos(v.vertex);o.uv=v.uv;o.color=v.color*_Color;return o;}
 fixed4 frag(F i):SV_Target {UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);return fixed4(i.color.rgb,i.color.a*tex2D(_MainTex,i.uv).a);}
 ENDCG } }
}
