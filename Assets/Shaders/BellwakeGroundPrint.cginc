// The four channels hold original meadow, trail, slate and snow paintings.
// World coordinates keep the texels at the same physical size on every map.
float2 BellwakeBrushUV(float2 metres)
{
    return float2(metres.x*.438+metres.y*.193, metres.y*.438-metres.x*.193);
}
float3 BellwakeGroundPrint(float3 paint, float4 marks, float profile)
{
    float detail = marks.b;
    if (profile < 0.5) {
        float green = smoothstep(.83, 1.07, paint.g / max(.001, paint.r));
        float warm = 1.0-smoothstep(.79, 1.04, paint.b / max(.001, paint.g));
        detail = lerp(marks.g, marks.r, green * warm);
    } else if (profile < 1.5) {
        detail = marks.g;
    } else if (profile > 2.5) {
        detail = marks.a;
    }
    return paint * (1.0 + (detail - .5) * .76);
}
