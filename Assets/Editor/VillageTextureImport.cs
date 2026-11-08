using UnityEditor;
using UnityEngine;
namespace Wizzard.Editor
{
    public sealed class VillageTextureImport : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            if(assetPath.StartsWith("Assets/Resources/VillageMasks/"))
            {
                // This is scalar coverage data, not a painted surface tile.
                var mask=(TextureImporter)assetImporter;
                mask.textureType=TextureImporterType.Default;
                mask.maxTextureSize=1024;mask.mipmapEnabled=true;mask.sRGBTexture=false;
                mask.wrapMode=TextureWrapMode.Clamp;mask.filterMode=FilterMode.Bilinear;
                mask.anisoLevel=0;mask.alphaSource=TextureImporterAlphaSource.None;
                mask.textureCompression=TextureImporterCompression.Uncompressed;
                var settings=mask.GetDefaultPlatformTextureSettings();
                settings.format=TextureImporterFormat.R8;settings.maxTextureSize=1024;
                mask.SetPlatformTextureSettings(settings);
                return;
            }
            if(!assetPath.StartsWith("Assets/Resources/VillageTextures/")) return;
            var importer=(TextureImporter)assetImporter;
            importer.maxTextureSize=64;importer.mipmapEnabled=true;importer.sRGBTexture=true;
            importer.wrapMode=TextureWrapMode.Repeat;importer.filterMode=FilterMode.Bilinear;
            importer.anisoLevel=0;importer.textureCompression=TextureImporterCompression.Uncompressed;
            if(assetPath.EndsWith("/PathBlend.png"))
            {
                importer.mipMapsPreserveCoverage=true;
                importer.alphaTestReferenceValue=0.5f;
            }
        }
    }
}
