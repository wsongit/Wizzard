using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.XR;
using CommonUsages = UnityEngine.XR.CommonUsages;

namespace Wizzard
{
    // Original arm-driven controller. No Gorilla Tag source or assets are used.
    [RequireComponent(typeof(CharacterController))]
    public sealed class GorillaPlayer : MonoBehaviour
    {
        public Transform head, leftHand, rightHand, body;
        public float armLength=.95f, handRadius=.10f, launchMultiplier=1.15f, maxSpeed=8f;
        public bool MovementLocked { get; set; }
        public LayerMask surfaces=1<<MeadowWorld.GroundLayer;
        CharacterController motor;
        readonly Transform[] arms=new Transform[2];
        readonly Vector3[] previous=new Vector3[2];
        readonly Vector3[] targets=new Vector3[2];
        readonly bool[] touching=new bool[2];
        readonly bool[] tracked=new bool[2];
        public bool PalmTracked(int side) => XRSettings.isDeviceActive && tracked[side];
        Vector3 velocity, smoothedVelocity;
        float yaw, pitch; bool turnReady=true, initialized;
        const float headGuardRadius=.12f;
        Vector3 lastClearHead;
        bool hasClearHead, headBlocked;
        public bool HeadObstructed => headBlocked;
        Renderer headGuardRenderer;
        Material headGuardMaterial;
        void Awake()
        {
            motor=GetComponent<CharacterController>();
            motor.minMoveDistance=0;
            for(int i=0;i<2;i++)
                arms[i]=BellwakeModels.Create("RunnerArm",transform).transform;
        }
        void Update()
        {
            float dt=Mathf.Min(Time.deltaTime,.033f); if(dt<=0) return;
            bool vr=XRSettings.isDeviceActive;
            if(vr) ReadHead(); else DesktopLook();
            if(MovementLocked) { UpdateHeadGuard(vr); return; }
            for (int i = 0; i < 2; i++)
            {
                bool hadPose = tracked[i];
                targets[i] = HandTarget(i == 0 ? XRNode.LeftHand : XRNode.RightHand, i, vr);
                if (!initialized || !hadPose) previous[i] = targets[i];
            }
            initialized = true;
            Vector3 start=transform.position, push=Vector3.zero; int contacts=0;
            bool hadContact=touching[0]||touching[1];
            bool lostPlantedHand = false;
            for(int i=0;i<2;i++)
            {
                if (!tracked[i])
                {
                    lostPlantedHand |= touching[i];
                    touching[i] = false;
                    continue;
                }
                bool hit = FindPalmContact(previous[i], targets[i], touching[i], out Vector3 anchor);
                touching[i]=hit;
                if(hit) { push+=anchor-targets[i]; contacts++; previous[i]=anchor; }
                else previous[i]=targets[i];
            }
            if(contacts>0)
            {
                velocity=Vector3.zero;
                if(!hadContact) smoothedVelocity=Vector3.zero;
                motor.Move(Vector3.ClampMagnitude(push/contacts,.3f));
                smoothedVelocity=Vector3.Lerp(smoothedVelocity,(transform.position-start)/dt,.4f);
            }
            else
            {
                if(hadContact && !lostPlantedHand)
                    velocity=Vector3.ClampMagnitude(smoothedVelocity*launchMultiplier,maxSpeed);
                if(motor.isGrounded && velocity.y<0) velocity.y=-1;
                velocity+=Physics.gravity*dt;
                Vector3 desktop=Vector3.zero;
                if(!vr && Keyboard.current!=null)
                {
                    var k=Keyboard.current;
                    desktop=(transform.right*((k.dKey.isPressed?1:0)-(k.aKey.isPressed?1:0))+
                        transform.forward*((k.wKey.isPressed?1:0)-(k.sKey.isPressed?1:0)))*4;
                    if(k.spaceKey.wasPressedThisFrame && motor.isGrounded) velocity.y=5;
                }
                var flags=motor.Move((velocity+desktop)*dt);
                if((flags&CollisionFlags.Above)!=0) velocity.y=Mathf.Min(0,velocity.y);
                if((flags&CollisionFlags.Sides)!=0) { velocity.x=0; velocity.z=0; }
            }
            for(int i=0;i<2;i++)
            {
                var hand=i==0?leftHand:rightHand;
                hand.position=touching[i]?previous[i]:targets[i]+(transform.position-start);
                if(!touching[i]) previous[i]=hand.position;
            }
            body.position=head.position+Vector3.down*.65f;
            body.rotation=Quaternion.Euler(0,head.eulerAngles.y,0);
            for(int i=0;i<2;i++)
            {
                Vector3 shoulder=body.position+body.right*(i==0?-.27f:.27f)+Vector3.up*.18f;
                Vector3 palm=(i==0?leftHand:rightHand).position;
                arms[i].position=(shoulder+palm)*.5f;
                arms[i].up=shoulder-palm;
                arms[i].localScale=new Vector3(1,Vector3.Distance(shoulder,palm),1);
            }
            if(vr) SnapTurn();
            if(head.position.y < -30) ResetPlayer();
            UpdateHeadGuard(vr);
        }
        bool FindPalmContact(Vector3 previousPalm, Vector3 target, bool planted, out Vector3 anchor)
        {
            anchor = previousPalm;
            Vector3 delta = target - previousPalm;
            if (delta.sqrMagnitude > .000001f && Physics.SphereCast(previousPalm, handRadius,
                delta.normalized, out RaycastHit hit, delta.magnitude + .015f, surfaces, QueryTriggerInteraction.Ignore))
            {
                anchor = hit.point + hit.normal * (handRadius + .01f);
                return true;
            }
            // Check where the controller is now. The old anchor stays next to
            // the surface even after the player has lifted their hand away.
            return planted && delta.sqrMagnitude < .16f &&
                Physics.CheckSphere(target, handRadius + .025f, surfaces, QueryTriggerInteraction.Ignore);
        }
        void ReadHead()
        {
            var device=InputDevices.GetDeviceAtXRNode(XRNode.Head);
            bool valid=device.isValid && device.TryGetFeatureValue(CommonUsages.isTracked,out bool tracking) && tracking;
            if(!valid) return;
            if(device.TryGetFeatureValue(CommonUsages.devicePosition,out Vector3 p)) ApplyTrackedHeadPosition(p);
            if(device.TryGetFeatureValue(CommonUsages.deviceRotation,out Quaternion q)) head.localRotation=q;
        }
        void ApplyTrackedHeadPosition(Vector3 position)
        {
            // Seed the guard before the first tracked pose too, so a standing-height
            // change immediately after arrival cannot skip a low ceiling.
            if(!hasClearHead && !Physics.CheckSphere(head.position,headGuardRadius,surfaces,QueryTriggerInteraction.Ignore))
            { lastClearHead=head.position; hasClearHead=true; }
            // Sweep while the capsule is still at the previous tracked horizontal centre.
            // Changing centre alone teleports a CharacterController through thin walls.
            Vector3 oldOffset=new Vector3(motor.center.x,0,motor.center.z);
            Vector3 nextOffset=new Vector3(position.x,0,position.z);
            Vector3 request=transform.TransformVector(nextOffset-oldOffset);
            motor.height=Mathf.Clamp(position.y+.1f,.6f,2.4f);
            motor.center=new Vector3(oldOffset.x,motor.height*.5f,oldOffset.z);
            if(motor.enabled && request.sqrMagnitude>0)
            {
                motor.Move(request);
                // Rebase origin and centre together. In free space these cancel exactly;
                // at a wall only the allowed displacement reaches the head and body.
                transform.position-=request;
            }
            motor.center=new Vector3(nextOffset.x,motor.height*.5f,nextOffset.z);
            head.localPosition=position;
        }
        void UpdateHeadGuard(bool vr)
        {
            if(!vr)
            {
                hasClearHead=false; headBlocked=false;
                if(headGuardRenderer!=null) { headGuardMaterial.color=Color.clear; headGuardRenderer.enabled=false; }
                return;
            }
            Vector3 current=head.position;
            headBlocked=Physics.CheckSphere(current,headGuardRadius,surfaces,QueryTriggerInteraction.Ignore);
            if(hasClearHead && !headBlocked)
            {
                Vector3 travel=current-lastClearHead;
                if(travel.sqrMagnitude>.000001f)
                    headBlocked=Physics.SphereCast(lastClearHead,headGuardRadius,travel.normalized,
                        out _,travel.magnitude,surfaces,QueryTriggerInteraction.Ignore);
            }
            // Keep the last clear point while obstructed: overlap queries alone stop
            // reporting a closed MeshCollider once the head is completely inside it.
            if(!headBlocked) { lastClearHead=current; hasClearHead=true; }
            if(headGuardRenderer==null && headBlocked)
            {
                var cover=GameObject.CreatePrimitive(PrimitiveType.Quad);
                cover.name="Head collision occlusion"; Destroy(cover.GetComponent<Collider>());
                cover.transform.SetParent(head,false); cover.transform.localPosition=Vector3.forward*.25f;
                cover.transform.localScale=Vector3.one*10;
                headGuardMaterial=new Material(Shader.Find("Wizzard/VillageFade"));
                headGuardMaterial.renderQueue=5000;
                headGuardRenderer=cover.GetComponent<Renderer>();
                headGuardRenderer.sharedMaterial=headGuardMaterial;
            }
            if(headGuardRenderer!=null)
            {
                // Instant cover prevents seeing through surfaces; fade back after retreat.
                float alpha=headBlocked?1:Mathf.MoveTowards(headGuardMaterial.color.a,0,Time.unscaledDeltaTime*6);
                headGuardMaterial.color=new Color(0,0,0,alpha);
                headGuardRenderer.enabled=alpha>0;
            }
        }
        void OnDestroy()
        {
            if(headGuardMaterial!=null) Destroy(headGuardMaterial);
        }
        Vector3 HandTarget(XRNode node,int i,bool vr)
        {
            Vector3 local=new Vector3(i==0?-.35f:.35f,1,.4f);
            tracked[i]=!vr;
            if(vr)
            {
                var device=InputDevices.GetDeviceAtXRNode(node);
                tracked[i]=device.isValid && device.TryGetFeatureValue(CommonUsages.isTracked,out bool t) && t;
                if(tracked[i] && device.TryGetFeatureValue(CommonUsages.devicePosition,out Vector3 p)) local=p;
                else tracked[i]=false;
                if(tracked[i] && device.TryGetFeatureValue(CommonUsages.deviceRotation,out Quaternion rotation))
                    (i==0?leftHand:rightHand).rotation=transform.rotation*rotation;
            }
            else if(Mouse.current!=null)
            {
                bool pressed=i==0?Mouse.current.leftButton.isPressed:Mouse.current.rightButton.isPressed;
                if(pressed) local.y=.08f;
            }
            Vector3 shoulder=head.position+transform.TransformDirection(new Vector3(i==0?-.18f:.18f,-.25f,0));
            return shoulder+Vector3.ClampMagnitude(transform.TransformPoint(local)-shoulder,armLength);
        }
        void DesktopLook()
        {
            if(Mouse.current==null || Keyboard.current==null) return;
            if(Keyboard.current.escapeKey.wasPressedThisFrame) Cursor.lockState=CursorLockMode.None;
            if(Mouse.current.middleButton.wasPressedThisFrame) Cursor.lockState=CursorLockMode.Locked;
            if(Cursor.lockState!=CursorLockMode.Locked) return;
            var d=Mouse.current.delta.ReadValue(); yaw+=d.x*.12f; pitch=Mathf.Clamp(pitch-d.y*.12f,-75,75);
            transform.rotation=Quaternion.Euler(0,yaw,0); head.localRotation=Quaternion.Euler(pitch,0,0);
        }
        void SnapTurn()
        {
            var device=InputDevices.GetDeviceAtXRNode(XRNode.RightHand);
            if(!device.TryGetFeatureValue(CommonUsages.primary2DAxis,out Vector2 axis)) return;
            if(Mathf.Abs(axis.x)<.3f) turnReady=true;
            if(turnReady && Mathf.Abs(axis.x)>.75f)
            {
                transform.RotateAround(head.position,Vector3.up,Mathf.Sign(axis.x)*45);
                for(int i=0;i<2;i++) touching[i]=false;
                initialized=false; smoothedVelocity=Vector3.zero; turnReady=false;
            }
        }
        public void ResetPlayer()
        {
            Teleport(new Vector3(0,MeadowWorld.Height(0,0)+.2f,0),Quaternion.identity);
        }
        public event System.Action<Vector3> Teleporting;
        public void Teleport(Vector3 position,Quaternion rotation)
        {
            Teleporting?.Invoke(position);
            motor.enabled=false;
            transform.rotation=rotation; yaw=rotation.eulerAngles.y;
            // Put the physical head over the destination despite room-scale offsets.
            Vector3 offset=transform.TransformVector(new Vector3(head.localPosition.x,0,head.localPosition.z));
            transform.position=position-offset;
            motor.height=Mathf.Clamp(head.localPosition.y+.1f,.6f,2.4f);
            motor.center=new Vector3(head.localPosition.x,motor.height*.5f,head.localPosition.z);
            motor.enabled=true; velocity=smoothedVelocity=Vector3.zero; initialized=false;
            hasClearHead=false; headBlocked=false;
            if(headGuardRenderer!=null) { headGuardMaterial.color=Color.clear; headGuardRenderer.enabled=false; }
            touching[0]=touching[1]=false;
        }
    }
}
