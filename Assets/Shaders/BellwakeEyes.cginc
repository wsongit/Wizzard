// Atlas and time are shared by Unity and WebXR. Pixel coordinates use the
// painting's top-left origin. Each resident's eye strip has its own timer.
float2 BellwakeEyes(float2 pixel, float seconds)
{
    float2 tile = floor(pixel / 64.0);
    bool leftPortrait = tile.x < 4.0 && tile.y < 2.0;
    if (!leftPortrait && tile.x < 4.0) return pixel;
    float face = leftPortrait ? tile.x + 4.0 * tile.y : 4.0 + tile.x + 4.0 * tile.y;
    if (face > 36.0) return pixel;
    float2 local = pixel - tile * 64.0;
    float eyeX = abs(local.x - 32.5);
    if (local.y < 23.0 || local.y >= 36.0 || eyeX < 3.5 || eyeX >= 24.5) return pixel;

    float cycle = 3.35 + (face - floor(face / 7.0) * 7.0) * 0.19;
    float shifted = seconds + face * 0.813;
    float beat = shifted - cycle * floor(shifted / cycle);
    if (beat >= 0.205) return pixel;

    float pose = (beat >= 0.052 && beat < 0.144) ? 1.0 : 0.0;
    float slot = face * 2.0 + pose;
    float row = floor(slot / 19.0);
    float column = slot - 19.0 * row;
    // The sawyer's 64-pixel portrait occupies x=256..319 in the last four rows.
    float start = column < 11.0 ? column * 23.0 : 320.0 + (column - 11.0) * 23.0;
    return float2(start + 1.0 + eyeX - 3.5, 449.0 + row * 16.0 + local.y - 23.0);
}
