Shader "Wizzard/BellwakeSky" {
 Properties { _Panorama ("Painted sky", Cube) = "" {} _Stars ("Star field", Cube) = "" {} }
 SubShader { Tags { "Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox" }
 Cull Off ZWrite Off
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #pragma multi_compile_instancing
 #pragma multi_compile_local __ BELLWAKE_OUTDOOR_SKY
 #include "UnityCG.cginc"
 struct V { float4 vertex:POSITION; UNITY_VERTEX_INPUT_INSTANCE_ID };
 struct F { float4 pos:SV_POSITION; float3 dir:TEXCOORD0; UNITY_VERTEX_OUTPUT_STEREO };
 samplerCUBE _Panorama, _Stars;
 half _BellwakeNight, _BellwakeDusk;
 float3 _BellwakeSunDir;
 F vert(V v){
     F o;UNITY_SETUP_INSTANCE_ID(v);UNITY_INITIALIZE_OUTPUT(F,o);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
     o.pos=UnityObjectToClipPos(v.vertex);o.dir=v.vertex.xyz;return o;
 }
 fixed4 frag(F i):SV_Target {
     UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
     float3 d=normalize(i.dir);
     half3 sky=texCUBE(_Panorama,d).rgb;
     #ifdef BELLWAKE_OUTDOOR_SKY
     half dusk=_BellwakeDusk*saturate(1.15-2*abs(d.y));
     sky=lerp(sky,sky*half3(1.04,.64,.64)+half3(.16,.029,.006),dusk*.72);
     sky*=lerp(half3(1,1,1),half3(.045,.069,.145),_BellwakeNight);
     float solar=dot(d,_BellwakeSunDir);
     half above=smoothstep(.18,.28,d.y);
     float sun=smoothstep(.99930,.99952,solar)*(1-_BellwakeNight);
     float moon=smoothstep(.99947,.99965,-solar)*_BellwakeNight;
     sky+=above*(sun*half3(.9,.67,.34)+moon*half3(.58,.67,.79));
     UNITY_BRANCH if (_BellwakeNight>.005)
         sky+=texCUBE(_Stars,d).rgb * above * _BellwakeNight;
     #else
     sky*=lerp(half3(1,1,1),half3(.12,.18,.36),_BellwakeNight);
     #endif
     return half4(sky,1);
 }
 ENDCG } }
}
