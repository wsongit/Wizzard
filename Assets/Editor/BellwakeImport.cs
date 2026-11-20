using UnityEditor;
using UnityEngine;

namespace Wizzard.Editor
{
    public sealed class BellwakeImport : AssetPostprocessor
    {
        public override uint GetVersion() => 4;
        void OnPostprocessModel(GameObject model)
        {
            if (!IsBellwakeModel()) return;
            var meshes = model.GetComponentsInChildren<MeshFilter>(true);
            if (!assetPath.Contains("/Field/") && !System.Array.Exists(meshes, mesh => mesh.name=="Terrain")) return;
            foreach (var mesh in meshes)
            {
                if (!BellwakeCampaign.IsCollisionSurface(mesh.name)) continue;
                if (!mesh.TryGetComponent<MeshCollider>(out var surface))
                    surface=mesh.gameObject.AddComponent<MeshCollider>();
                surface.sharedMesh=mesh.sharedMesh;
                mesh.gameObject.layer=MeadowWorld.GroundLayer;
            }
        }
        bool IsBellwakeModel()
        {
            return assetPath.StartsWith("Assets/Resources/Bellwake/Rooms/") ||
                assetPath.StartsWith("Assets/Resources/Bellwake/Wayfarer/") ||
                assetPath.StartsWith("Assets/Resources/Bellwake/Field/");
        }
        void OnPreprocessModel()
        {
            if (!IsBellwakeModel())
                return;
            var model = (ModelImporter)assetImporter;
            model.importAnimation = false;
            model.animationType = ModelImporterAnimationType.None;
            model.importCameras = false;
            model.importLights = false;
            model.preserveHierarchy = true;
            model.importNormals = ModelImporterNormals.Import;
            model.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
            model.materialName = ModelImporterMaterialName.BasedOnMaterialName;
            model.materialLocation = ModelImporterMaterialLocation.InPrefab;
            model.isReadable = true; // MeshCollider cooking also works on mirrored FBX transforms.
        }
        void OnPreprocessTexture()
        {
            if (assetPath.StartsWith("Assets/Resources/Bellwake/Skies/"))
            {
                var sky = (TextureImporter)assetImporter;
                sky.textureShape = TextureImporterShape.TextureCube;
                sky.generateCubemap = TextureImporterGenerateCubemap.Cylindrical;
                sky.mipmapEnabled = false;
                sky.filterMode = FilterMode.Bilinear;
                return;
            }
            if (assetPath.StartsWith("Assets/Resources/Bellwake/Letters/"))
            {
                var page = (TextureImporter)assetImporter;
                page.npotScale = TextureImporterNPOTScale.None;
                page.wrapMode = TextureWrapMode.Clamp;
                page.filterMode = assetPath.EndsWith("/BellrootDawn.png") ? FilterMode.Point : FilterMode.Bilinear;
                return;
            }
            if (!assetPath.StartsWith("Assets/Resources/Bellwake/Textures/"))
                return;
            var tile = (TextureImporter)assetImporter;
            if (assetPath.EndsWith("/ProvisionStamps.png") || assetPath.EndsWith("/PocketGlyphs.png") || assetPath.EndsWith("/Letterpress.png"))
            {
                tile.npotScale=TextureImporterNPOTScale.None;
                tile.filterMode=FilterMode.Point;
                tile.wrapMode=TextureWrapMode.Clamp;
                tile.mipmapEnabled=false;
                tile.alphaIsTransparency=true;
                tile.textureCompression=TextureImporterCompression.Uncompressed;
                return;
            }
            if (assetPath.EndsWith("Survey.png") || assetPath.EndsWith("Signs.png") || assetPath.EndsWith("/MarketNotices.png"))
                tile.npotScale = TextureImporterNPOTScale.None;
            if (assetPath.EndsWith("/RoadSorrel.png") || assetPath.EndsWith("/BanksidePlants.png"))
            {
                tile.alphaIsTransparency = true;
                tile.mipMapsPreserveCoverage = true;
                tile.alphaTestReferenceValue = .45f;
            }
            if (assetPath.EndsWith("/GroundBrush.png"))
            {
                tile.sRGBTexture = false;
                tile.alphaIsTransparency = false;
                tile.alphaSource = TextureImporterAlphaSource.FromInput;
            }
            tile.mipmapEnabled = true;
            tile.wrapMode = TextureWrapMode.Repeat;
            tile.filterMode = assetPath.EndsWith("/GroundBrush.png") ? FilterMode.Trilinear : FilterMode.Bilinear;
            tile.anisoLevel = 2;
            tile.textureCompression = TextureImporterCompression.Uncompressed;
        }
    }
}
