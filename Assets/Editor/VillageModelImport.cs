using UnityEditor;
namespace Wizzard.Editor
{
    // Runtime builds collision meshes and reads marker submeshes on Quest as well as in Editor.
    public sealed class VillageModelImport : AssetPostprocessor
    {
        void OnPreprocessModel()
        {
            if(assetPath!="Assets/Resources/Village/Mossbell.obj") return;
            var importer=(ModelImporter)assetImporter;
            importer.isReadable=true;
            importer.globalScale=1;
            importer.meshCompression=ModelImporterMeshCompression.Off;
            importer.generateSecondaryUV=false;
            importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
            importer.importNormals=ModelImporterNormals.Import;
        }
    }
}
