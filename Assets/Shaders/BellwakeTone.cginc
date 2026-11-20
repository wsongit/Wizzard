#ifndef WIZZARD_BELLWAKE_TONE
#define WIZZARD_BELLWAKE_TONE
half _BellwakeNight, _BellwakeDusk;
half3 WizzardSurfaceLight(half3 paint, half shade, half glow, half window)
{
    half3 lantern = half3(.91,.38,.072) * (.35 + saturate(paint.r * 3.0));
    half3 evening = lerp(half3(1,1,1),half3(1.07,.93,.82),_BellwakeDusk);
    half3 moon = lerp(evening,half3(.14,.22,.40),_BellwakeNight * (1-glow));
    half3 lit = paint * lerp(shade,1.32,glow) * moon;
    return lerp(lit,lantern,window * _BellwakeNight);
}
#endif
