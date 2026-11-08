using System;
using System.Reflection;
using UnityEditor;
using UnityEngine;

namespace Wizzard.Editor
{
    // Exercises real Unity collision, without needing an XR device or a test package.
    // Run in Play mode; all test objects are temporary and separate from the live player.
    public static class RoomScaleCollisionCheck
    {
        [MenuItem("Wizzard/Validate room-scale wall collision")]
        public static void Validate()
        {
            if(!EditorApplication.isPlaying)
                throw new InvalidOperationException("Enter Play mode before running the room-scale collision check.");
            var root=new GameObject("Temporary room-scale collision test");
            try
            {
                var floor=Cube(root.transform,"Test floor",new Vector3(5000,-.5f,5000),new Vector3(20,1,20));
                var wall=Cube(root.transform,"Thin wall",new Vector3(5001,1.5f,5000),new Vector3(.2f,3,4));
                var rig=new GameObject("Test rig"); rig.transform.SetParent(root.transform,false);
                rig.transform.position=new Vector3(5000,.05f,5000);
                var motor=rig.AddComponent<CharacterController>();
                motor.radius=.22f; motor.height=1.75f; motor.center=new Vector3(0,.875f,0);
                motor.skinWidth=.02f; motor.stepOffset=.15f; motor.minMoveDistance=0;
                var head=new GameObject("Test tracked head");head.transform.SetParent(rig.transform,false);
                head.transform.localPosition=new Vector3(0,1.65f,0);
                var player=rig.AddComponent<GorillaPlayer>();player.enabled=false;player.head=head.transform;
                // Awake schedules arm colliders for destruction at end of frame. This
                // synchronous check must remove them before exercising the controller.
                foreach(var collider in rig.GetComponentsInChildren<Collider>())
                    if(collider!=motor) UnityEngine.Object.DestroyImmediate(collider);
                Physics.SyncTransforms();
                var apply=typeof(GorillaPlayer).GetMethod("ApplyTrackedHeadPosition",BindingFlags.Instance|BindingFlags.NonPublic);
                var guard=typeof(GorillaPlayer).GetMethod("UpdateHeadGuard",BindingFlags.Instance|BindingFlags.NonPublic);
                var blocked=typeof(GorillaPlayer).GetField("headBlocked",BindingFlags.Instance|BindingFlags.NonPublic);
                Require(apply!=null && guard!=null && blocked!=null,"Collision check hooks are missing.");

                apply.Invoke(player,new object[]{new Vector3(2,1.65f,0)});
                Physics.SyncTransforms();
                Require(Mathf.Abs(head.transform.localPosition.x-2)<.001f,"Tracked local head position was altered.");
                Require(head.transform.position.x<5000.82f,"Room-scale head crossed a thin wall.");
                Require(Mathf.Abs(motor.bounds.center.x-head.transform.position.x)<.03f,"Capsule and head separated after wall contact.");

                player.Teleport(new Vector3(5000,.05f,5005),Quaternion.identity);
                Vector3 start=rig.transform.position; float headX=head.transform.position.x;
                apply.Invoke(player,new object[]{new Vector3(3,1.65f,0)});
                Require(Vector3.Distance(start,rig.transform.position)<.015f,"Unobstructed physical motion moved the XR origin.");
                Require(Mathf.Abs(head.transform.position.x-headX-1)<.015f,"Free head movement was not preserved.");

                player.Teleport(new Vector3(5000,.05f,5005),Quaternion.Euler(0,90,0));
                Vector3 before=head.transform.position;
                apply.Invoke(player,new object[]{new Vector3(3.5f,1.65f,0)});
                Require(Vector3.Distance(head.transform.position-before,Vector3.back*.5f)<.015f,"Rotated tracking axes were reconciled incorrectly.");

                var ceiling=Cube(root.transform,"Low ceiling",new Vector3(5000,2.05f,5005),new Vector3(4,.2f,4));
                player.Teleport(new Vector3(5000,.05f,5005),Quaternion.identity);
                Physics.SyncTransforms();guard.Invoke(player,new object[]{true});
                Require(!(bool)blocked.GetValue(player),"Clear head position incorrectly obstructed.");
                apply.Invoke(player,new object[]{new Vector3(3.5f,2.5f,0)});
                guard.Invoke(player,new object[]{true});
                Require((bool)blocked.GetValue(player),"Standing through a ceiling did not cover the view.");
                guard.Invoke(player,new object[]{true});
                Require((bool)blocked.GetValue(player),"Mask cleared while fully beyond the ceiling.");
                apply.Invoke(player,new object[]{new Vector3(3.5f,1.65f,0)});
                guard.Invoke(player,new object[]{true});
                Require(!(bool)blocked.GetValue(player),"Retreating to clear space did not release the mask.");
                player.Teleport(new Vector3(5000,.05f,5005),Quaternion.identity);
                apply.Invoke(player,new object[]{new Vector3(3.5f,2.5f,0)});
                guard.Invoke(player,new object[]{true});
                Require((bool)blocked.GetValue(player),"First tracked pose after teleport skipped ceiling protection.");
                Debug.Log("PASS: room-scale thin-wall sweep, free motion, rotated tracking, capsule alignment and ceiling occlusion. Physical headset comfort still needs device testing.");
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
        static GameObject Cube(Transform parent,string name,Vector3 position,Vector3 scale)
        {
            var obj=GameObject.CreatePrimitive(PrimitiveType.Cube);obj.name=name;
            obj.layer=MeadowWorld.GroundLayer;obj.transform.SetParent(parent,false);
            obj.transform.position=position;obj.transform.localScale=scale;return obj;
        }
        static void Require(bool value,string message)
        {
            if(!value) throw new InvalidOperationException(message);
        }
    }
}
