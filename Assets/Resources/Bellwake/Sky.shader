Shader "Wizzard/BellwakeSky" {
 Properties { _Panorama ("Painted sky", Cube) = "" {} }
 SubShader { Tags { "Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox" }
 Cull Off ZWrite Off
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_instancing
 #include "UnityCG.cginc"
 struct V { float4 vertex:POSITION; UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct F { float4 pos:SV_POSITION; float3 dir:TEXCOORD0; UNITY_VERTEX_OUTPUT_STEREO };
 samplerCUBE _Panorama; half _BellwakeNight;
 F vert(V v){F o;UNITY_SETUP_INSTANCE_ID(v);UNITY_INITIALIZE_OUTPUT(F,o);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);o.pos=UnityObjectToClipPos(v.vertex);o.dir=v.vertex.xyz;return o;}
 fixed4 frag(F i):SV_Target {UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);fixed4 paint=texCUBE(_Panorama,i.dir);paint.rgb*=lerp(half3(1,1,1),half3(.12,.18,.36),_BellwakeNight);return paint;}
 ENDCG } }
}
