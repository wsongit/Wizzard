using System;
using UnityEngine;

namespace Wizzard
{
    internal static class BellwakeCheckpoint
    {
        const string Backup = ".previous";

        public static bool Exists(string slot)
        {
            return PlayerPrefs.HasKey(slot) || PlayerPrefs.HasKey(slot + Backup);
        }

        static BellwakeJourney Decode(string json)
        {
            if (string.IsNullOrEmpty(json)) return null;
            try
            {
                // A syntactically valid but empty object must not replace a playable save.
                var journey = new BellwakeJourney { version = 0 };
                JsonUtility.FromJsonOverwrite(json, journey);
                return journey.Valid() ? journey : null;
            }
            catch (ArgumentException)
            {
                return null;
            }
        }

        public static BellwakeJourney Read(string slot, out string checkpoint)
        {
            checkpoint = PlayerPrefs.GetString(slot, "");
            var journey = Decode(checkpoint);
            if (journey != null) return journey;

            checkpoint = PlayerPrefs.GetString(slot + Backup, "");
            journey = Decode(checkpoint);
            if (journey != null)
            {
                PlayerPrefs.SetString(slot, checkpoint);
                PlayerPrefs.Save();
                Debug.LogWarning("Bellwake restored the previous checkpoint for this save file.");
                return journey;
            }
            if (Exists(slot)) Debug.LogWarning("Bellwake could not read either checkpoint for this save file.");
            checkpoint = null;
            return new BellwakeJourney();
        }

        // Both values are committed together with the caller's other pending preferences.
        public static void Write(string slot, string next, string previous)
        {
            PlayerPrefs.SetString(slot + Backup, previous ?? next);
            PlayerPrefs.SetString(slot, next);
        }
    }
}
