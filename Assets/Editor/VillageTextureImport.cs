using UnityEditor;
using UnityEngine;
namespace Wizzard.Editor
{
    public sealed class VillageTextureImport : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
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
