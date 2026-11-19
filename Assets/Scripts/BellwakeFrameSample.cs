using System;
using UnityEngine;

namespace Wizzard
{
    // Development APKs measure Unity frame intervals. Headset compositor timing is separate.
    public sealed class BellwakeFrameSample : MonoBehaviour
    {
        readonly float[] frames = new float[360];
        string room;
        BellwakeField field;
        float warmup;
        int count;
        bool travelling;
        float loadStart, worstFrame;
        public void StartTravel()
        {
            field = null;
            travelling = true;
            loadStart = Time.realtimeSinceStartup;
            worstFrame = 0;
            enabled = true;
        }
        public void Begin(string name, BellwakeField activeField = null)
        {
            if (travelling)
                Debug.LogFormat("Bellwake loaded {0} in {1:F0} ms including fades. Worst transition frame {2:F1} ms. Allocated {3:F1} MiB.",
                    name, (Time.realtimeSinceStartup-loadStart)*1000, worstFrame,
                    UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong() / 1048576f);
            travelling = false;
            room = name;
            field = activeField;
            warmup = Time.unscaledTime + (field == null ? 3 : 0);
            count = 0;
            enabled = true;
        }
        void Update()
        {
            if (travelling)
            {
                worstFrame = Mathf.Max(worstFrame, Time.unscaledDeltaTime * 1000);
                return;
            }
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
            if (field == null)
            {
                enabled = false;
                return;
            }
            Debug.LogFormat("Bellwake field: {0} resident, {1} loaded, {2} retired, {3} memory sweeps this visit. Unity allocated {4:F1} MiB.",
                field.LoadedCells - field.RetiredCells, field.LoadedCells, field.RetiredCells, field.CompletedSweeps,
                UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong() / 1048576f);
            count = 0;
        }
    }
}
