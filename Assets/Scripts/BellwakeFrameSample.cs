using System;
using UnityEngine;

namespace Wizzard
{
    // Development APKs report the actual presentation interval after room loading.
    public sealed class BellwakeFrameSample : MonoBehaviour
    {
        readonly float[] frames = new float[360];
        string room;
        float warmup;
        int count;
        public void Begin(string name)
        {
            room = name;
            warmup = Time.unscaledTime + 3;
            count = 0;
            enabled = true;
        }
        void Update()
        {
            if (Time.unscaledTime < warmup)
                return;
            frames[count++] = Time.unscaledDeltaTime * 1000;
            if (count < frames.Length)
                return;
            Array.Sort(frames);
            Debug.LogFormat("Bellwake frame intervals ({0}, {1}): median {2:F1} ms, p95 {3:F1} ms, max {4:F1} " +
                            "ms over {5} frames.",
                            room, SystemInfo.deviceModel, frames[count / 2], frames[(int)(count * .95f)],
                            frames[count - 1], count);
            enabled = false;
        }
    }
}
