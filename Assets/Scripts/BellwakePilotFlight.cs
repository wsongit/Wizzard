using UnityEngine;

namespace Wizzard
{
    // The saved perch is authoritative. The trip between its two posts is presentation.
    sealed class BellwakePilotFlight
    {
        readonly Transform body, left, right;
        readonly Transform[] posts;
        readonly Quaternion rest, leftRest, rightRest;
        readonly Vector3 north;
        readonly float duration;
        readonly AudioSource answer;
        Vector3 departure;
        int destination = -1;
        float elapsed;
        bool shown;
        public BellwakePilotFlight(Transform bird, Transform port, Transform starboard, Transform[] roosts, Vector3 modelNorth, float seconds, AudioClip call)
        {
            body=bird; left=port; right=starboard; posts=roosts; duration=seconds;
            north=Vector3.ProjectOnPlane(modelNorth,Vector3.up).normalized;
            rest=body.rotation;
            answer=body.gameObject.AddComponent<AudioSource>();
            answer.playOnAwake=false; answer.spatialBlend=1; answer.minDistance=9; answer.maxDistance=75;
            answer.dopplerLevel=.1f; answer.volume=.62f; answer.clip=call;
            left.SetParent(body,true); right.SetParent(body,true);
            leftRest=left.localRotation; rightRest=right.localRotation;
        }
        public void Update(int next, bool active, bool snap, float dt)
        {
            if (body.gameObject.activeSelf!=active) body.gameObject.SetActive(active);
            if (!active) { shown=false; return; }
            if (snap || !shown)
            {
                if (!shown) body.rotation=Quaternion.AngleAxis(180,Vector3.up)*rest;
                body.position=posts[next].position;
                elapsed=duration; destination=next; shown=true;
                left.localRotation=leftRest; right.localRotation=rightRest;
                return;
            }
            if (next!=destination)
            {
                if (answer.clip!=null) answer.Play();
                departure=body.position; destination=next; elapsed=0;
                Vector3 path=Vector3.ProjectOnPlane(posts[next].position-departure,Vector3.up);
                if (path.sqrMagnitude>.01f)
                    body.rotation=Quaternion.AngleAxis(Vector3.SignedAngle(north,path,Vector3.up),Vector3.up)*rest;
            }
            if (elapsed>=duration) return;
            elapsed=Mathf.Min(duration,elapsed+dt);
            float t=elapsed/duration, arc=Mathf.Sin(t*Mathf.PI);
            Vector3 perch=posts[destination].position;
            body.position=Vector3.Lerp(departure,perch,t*t*(3-2*t))+Vector3.up*(arc*Mathf.Min(4f,Vector3.Distance(departure,perch)*.20f));
            float beat=arc*(18f+34f*Mathf.Sin(t*Mathf.PI*12));
            left.localRotation=leftRest*Quaternion.Euler(0,0,beat);
            right.localRotation=rightRest*Quaternion.Euler(0,0,-beat);
        }
    }
}
