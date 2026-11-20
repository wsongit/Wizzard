import { LinearFilter, LinearMipmapLinearFilter } from "three";

// Match the Unity world's three-point magnification. At a distance, sample the
// ordinary anisotropic mip chain so small leaves and roof edges stay steady in VR.
const sampling = `
#ifdef USE_MAP
vec4 bellwakePaint(sampler2D pigment, vec2 uv) {
  vec2 size = vec2(textureSize(pigment, 0));
  vec2 dx = dFdx(uv), dy = dFdy(uv);
  vec2 sx = dx * size, sy = dy * size;
  float footprint = max(dot(sx, sx), dot(sy, sy));
  if (footprint >= 1.0) return textureGrad(pigment, uv, dx, dy);

  vec2 pixel = uv * size - 0.5;
  vec2 f = fract(pixel);
  float corner = step(1.0, f.x + f.y);
  vec2 weights = mix(f, 1.0 - f, corner);
  vec2 centreUV = (floor(pixel) + corner + 0.5) / size;
  vec2 stepUV = (1.0 - 2.0 * corner) / size;
  vec4 centre = textureLod(pigment, centreUV, 0.0);
  vec4 x = textureLod(pigment, centreUV + vec2(stepUV.x, 0.0), 0.0);
  vec4 y = textureLod(pigment, centreUV + vec2(0.0, stepUV.y), 0.0);
  vec4 paint = centre + (x - centre) * weights.x + (y - centre) * weights.y;
  if (footprint > 0.4225) {
    paint = mix(paint, textureGrad(pigment, uv, dx, dy), smoothstep(0.65, 1.0, sqrt(footprint)));
  }
  return paint;
}
#endif
`;

export function applyPaintFilter(shader) {
  shader.fragmentShader = shader.fragmentShader
    .replace("#include <map_pars_fragment>", "#include <map_pars_fragment>\n" + sampling)
    .replace("#include <map_fragment>", "#ifdef USE_MAP\n diffuseColor *= bellwakePaint(map, vMapUv);\n#endif");
}

// A lamp behind horn glass reveals the waviness that the painter put in the pane.
// diffuseColor already contains the filtered, linear-space pigment sample.
export function applyWindowFilter(shader) {
  applyPaintFilter(shader);
  shader.fragmentShader = shader.fragmentShader.replace("#include <emissivemap_fragment>",
    "#include <emissivemap_fragment>\n totalEmissiveRadiance *= 0.52 + 0.55 * clamp(dot(diffuseColor.rgb, vec3(.30, .59, .11)) * 5.0, 0.0, 1.0);");
}


export function preparePaint(material, name) {
  if (!material.map) return;
  material.onBeforeCompile = name === "WindowDark" || name === "WindowLight" ? applyWindowFilter : applyPaintFilter;
  if (name === "BanksidePlants" || name === "RoadSorrel") material.alphaTest = .45;
  material.map.magFilter = LinearFilter;
  material.map.minFilter = LinearMipmapLinearFilter;
  material.map.anisotropy = 2;
}
