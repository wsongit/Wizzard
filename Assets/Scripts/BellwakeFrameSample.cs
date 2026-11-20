using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;

namespace Wizzard
{
    // Development APKs measure Unity frame intervals. The compositor has its own timing.
    public sealed class BellwakeFrameSample : MonoBehaviour
    {
        readonly float[] frames = new float[360];
        readonly List<XRDisplaySubsystem> displays = new List<XRDisplaySubsystem>();
        string room;
        BellwakeField field;
        int count;
        bool travelling, paused, focused, suspended, skipNextFrame;
        double suspendedAt, suspendedSeconds, loadStart, warmupUntil;
        float worstFrame;

        double ActiveTime
        {
            get { return (suspended ? suspendedAt : Time.realtimeSinceStartupAsDouble) - suspendedSeconds; }
        }

        void OnEnable()
        {
            focused = Application.isFocused;
            UpdateSuspension();
            skipNextFrame = true;
        }

        void OnApplicationFocus(bool hasFocus)
        {
            focused = hasFocus;
            UpdateSuspension();
        }

        void OnApplicationPause(bool isPaused)
        {
            paused = isPaused;
            UpdateSuspension();
        }

        void UpdateSuspension()
        {
            bool shouldSuspend = paused || !focused;
            if (suspended == shouldSuspend) return;
            double now = Time.realtimeSinceStartupAsDouble;
            if (shouldSuspend) suspendedAt = now;
            else suspendedSeconds += now - suspendedAt;
            suspended = shouldSuspend;
            skipNextFrame = true;
        }

        public void StartTravel()
        {
            enabled = true;
            field = null;
            travelling = true;
            loadStart = ActiveTime;
            worstFrame = 0;
        }

        public void Begin(string name, BellwakeField activeField = null)
        {
            enabled = true;
            if (travelling)
                Debug.LogFormat("Bellwake loaded {0} in {1:F0} ms of active time including fades. Worst transition frame {2:F1} ms. Allocated {3:F1} MiB.",
                    name, (ActiveTime - loadStart) * 1000, worstFrame,
                    UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong() / 1048576f);
            travelling = false;
            room = name;
            field = activeField;
            warmupUntil = ActiveTime + (field == null ? 3 : 0);
            count = 0;
        }

        float RefreshRate(out bool measured)
        {
            displays.Clear();
            SubsystemManager.GetInstances(displays);
            foreach (var display in displays)
                if (display.running && display.TryGetDisplayRefreshRate(out float hz) && hz > 0)
                {
                    measured = true;
                    return hz;
                }
            measured = false;
            return Application.targetFrameRate > 0 ? Application.targetFrameRate : 72;
        }

        void Update()
        {
            if (suspended) return;
            if (skipNextFrame)
            {
                skipNextFrame = false;
                return;
            }
            float interval = Time.unscaledDeltaTime * 1000;
            if (travelling)
            {
                worstFrame = Mathf.Max(worstFrame, interval);
                return;
            }
            if (ActiveTime < warmupUntil) return;
            frames[count++] = interval;
            if (count < frames.Length) return;
            Array.Sort(frames);
            float hz = RefreshRate(out bool measured);
            int longFrames = 0;
            for (int i = count - 1; i >= 0 && frames[i] > 1500f / hz; i--) longFrames++;
            Debug.LogFormat("Bellwake frame intervals ({0}, {1}): median {2:F1} ms, p95 {3:F1} ms, max {4:F1} ms over {5} frames. " +
                            "{6} exceeded 1.5 frame periods at {7:F1} Hz ({8}).",
                            room, SystemInfo.deviceModel, frames[count / 2], frames[(int)Math.Ceiling(count * .95) - 1],
                            frames[count - 1], count, longFrames, hz, measured ? "display" : "target");
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
