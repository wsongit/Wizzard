import groundPrint from "../../../Assets/Shaders/BellwakeGroundPrint.cginc";
import kilnPaint from "../../../Assets/Shaders/BellwakeKiln.cginc";
import residentEyes from "../../../Assets/Shaders/BellwakeEyes.cginc";
import { LinearFilter, LinearMipmapLinearFilter } from "three";

// Match the Unity world's three-point magnification. At a distance, sample the
// ordinary anisotropic mip chain so small leaves and roof edges stay steady in VR.
const sampling = `
#ifdef USE_MAP
vec4 bellwakePaintGradient(sampler2D pigment, vec2 uv, vec2 dx, vec2 dy) {
  vec2 size = vec2(textureSize(pigment, 0));
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
vec4 bellwakePaint(sampler2D pigment, vec2 uv) {
  return bellwakePaintGradient(pigment, uv, dFdx(uv), dFdy(uv));
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


function applyShopFilter(shader) {
  applyPaintFilter(shader);
  // A shopfront has painted shelves and goods on the far side of the glass.
  shader.fragmentShader = shader.fragmentShader.replace("#include <emissivemap_fragment>",
    "#include <emissivemap_fragment>\n totalEmissiveRadiance *= diffuseColor.rgb * vec3(1.7, 1.45, 1.2);");
}

const paintSeconds = { value: 0 };

export function updatePaintClock(seconds) {
  paintSeconds.value = seconds;
}

function applyResidentFilter(shader) {
  applyPaintFilter(shader);
  shader.uniforms.residentSeconds = paintSeconds;
  shader.fragmentShader = shader.fragmentShader
    .replace("void main() {", "uniform float residentSeconds;\n" + residentEyes.replaceAll("float2","vec2") + "\nvoid main() {")
    .replace("bellwakePaint(map, vMapUv)", "bellwakePaintGradient(map, BellwakeEyes(vMapUv * 512.0, residentSeconds) / 512.0, dFdx(vMapUv), dFdy(vMapUv))");
}

function applyKilnFilter(shader) {
  applyPaintFilter(shader);
  shader.uniforms.kilnSeconds = paintSeconds;
  shader.vertexShader = shader.vertexShader
    .replace("void main() {", "uniform float kilnSeconds;\n" + kilnPaint.replaceAll("float2", "vec2") + "\nvoid main() {")
    .replace("#include <uv_vertex>", "#include <uv_vertex>\n vMapUv = BellwakeKiln(vMapUv, kilnSeconds);");
  // The glow and the diffuse surface must show the same frame of the coals.
  shader.fragmentShader = shader.fragmentShader.replace("#include <emissivemap_fragment>",
    "totalEmissiveRadiance *= diffuseColor.rgb;");
}

const groundFunctions = groundPrint.replaceAll("float2", "vec2")
  .replaceAll("float3", "vec3").replaceAll("float4", "vec4").replaceAll("lerp(", "mix(");

export function fitGroundBrush(material, texture, profile) {
  material.onBeforeCompile = shader => {
    applyPaintFilter(shader);
    shader.uniforms.groundBrush = { value: texture };
    shader.uniforms.groundProfile = { value: profile };
    shader.vertexShader = "varying vec2 groundMetres;\n" + shader.vertexShader
      .replace("#include <worldpos_vertex>", "#include <worldpos_vertex>\n groundMetres = (modelMatrix * vec4(transformed, 1.0)).xz;");
    shader.fragmentShader = "varying vec2 groundMetres; uniform sampler2D groundBrush; uniform float groundProfile;\n"
      + groundFunctions + "\n" + shader.fragmentShader
      .replace("diffuseColor *= bellwakePaint(map, vMapUv);",
        "diffuseColor *= bellwakePaint(map, vMapUv);\n diffuseColor.rgb = BellwakeGroundPrint(diffuseColor.rgb, texture2D(groundBrush, BellwakeBrushUV(groundMetres)), groundProfile);");
  };
}

export function preparePaint(material, name) {
  if (!material.map) return;
  material.onBeforeCompile = name === "WindowDark" || name === "WindowLight" ? applyWindowFilter : applyPaintFilter;
  if (name === "ShopWindows") material.onBeforeCompile = applyShopFilter;
  if (name === "KilnFire") material.onBeforeCompile = applyKilnFilter;
  if (name === "ResidentCloth") material.onBeforeCompile = applyResidentFilter;
  if (name === "BanksidePlants" || name === "RoadSorrel") material.alphaTest = .45;
  material.map.magFilter = LinearFilter;
  material.map.minFilter = LinearMipmapLinearFilter;
  material.map.anisotropy = 2;
}
