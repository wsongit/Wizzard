// Local coordinates stay inside the same two-texel gutter in all 16 frames.
float2 BellwakeKiln(float2 uv, float seconds)
{
    float2 source = floor(uv * 4.0);
    float index = source.x + source.y * 4.0 + floor(seconds * 8.0);
    index -= 16.0 * floor(index / 16.0);
    float row = floor(index / 4.0);
    float2 target = float2(index - 4.0 * row, row);
    return uv + (target-source) * 0.25;
}
