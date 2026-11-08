using System;
using UnityEditor;
using UnityEngine;

namespace Wizzard.Editor
{
    public static class VillageReview
    {
        [MenuItem("Wizzard/Capture village comparison")]
        public static void Capture()
        {
            var village=UnityEngine.Object.FindObjectOfType<MossbellVillage>();
            if(!Application.isPlaying || village==null || !village.ReviewActive)
                throw new InvalidOperationException("Play Meadow, press F8, and wait for the entrance review view first.");
            string directory=System.IO.Path.GetFullPath("Documentation/UnityCaptures");
            System.IO.Directory.CreateDirectory(directory);
            string path=System.IO.Path.Combine(directory,"village-entrance.png");
            village.CaptureReview(path);Debug.Log("Saved actual Unity comparison capture: "+path);
        }
    }
}
