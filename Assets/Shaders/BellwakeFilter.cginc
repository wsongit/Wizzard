#ifndef WIZZARD_BELLWAKE_FILTER
#define WIZZARD_BELLWAKE_FILTER

// The N64 interpolates one triangle of the four nearest texels. Use that footprint
// up close, then blend into the anisotropic mip chain before the texels get small.
fixed4 BellwakeTile(sampler2D tile, float2 uv, float4 texelSize, float2 dx, float2 dy)
{
    float2 du=dx*texelSize.zw, dv=dy*texelSize.zw;
    float footprintSq=max(dot(du,du),dot(dv,dv));
    UNITY_BRANCH if (footprintSq>=1.0)
        return tex2Dgrad(tile,uv,dx,dy);

    float2 texel=uv*texelSize.zw-.5;
    float2 f=frac(texel);
    bool upper=f.x+f.y>1;
    float corner=upper ? 1 : 0;
    float2 weights=upper ? 1.0-f : f;
    float2 at=(floor(texel)+corner+.5)*texelSize.xy;
    float2 delta=(1-2*corner)*texelSize.xy;
    fixed4 centre=tex2Dlod(tile,float4(at,0,0));
    fixed4 horizontal=tex2Dlod(tile,float4(at+float2(delta.x,0),0,0));
    fixed4 vertical=tex2Dlod(tile,float4(at+float2(0,delta.y),0,0));
    fixed4 colour=centre+(horizontal-centre)*weights.x+(vertical-centre)*weights.y;
    UNITY_BRANCH if (footprintSq>.4225)
        colour=lerp(colour,tex2Dgrad(tile,uv,dx,dy),smoothstep(.65,1.0,sqrt(footprintSq)));
    return colour;
}
#endif
