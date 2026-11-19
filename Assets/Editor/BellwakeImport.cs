using UnityEditor;
using UnityEngine;

namespace Wizzard.Editor
{
    public sealed class BellwakeImport : AssetPostprocessor
    {
        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith("Assets/Resources/Bellwake/Rooms/"))
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
            if (!assetPath.StartsWith("Assets/Resources/Bellwake/Textures/"))
                return;
            var tile = (TextureImporter)assetImporter;
            if (assetPath.EndsWith("Survey.png") || assetPath.EndsWith("Signs.png"))
                tile.npotScale = TextureImporterNPOTScale.None;
            tile.mipmapEnabled = true;
            tile.wrapMode = TextureWrapMode.Repeat;
            tile.filterMode = FilterMode.Bilinear;
            tile.anisoLevel = 2;
            tile.textureCompression = TextureImporterCompression.Uncompressed;
        }
    }
}
