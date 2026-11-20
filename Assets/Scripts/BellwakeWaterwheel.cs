using UnityEngine;

namespace Wizzard
{
    // Opening the mill channel accelerates the visible wheel. The swept collider is stationary.
    public sealed class BellwakeWaterwheel : MonoBehaviour
    {
        Vector3 localAxle;
        BellwakeJourney journey;
        float speed;
        public void Initialize(Vector3 axis,BellwakeJourney story)
        {
            localAxle=transform.InverseTransformDirection(axis).normalized;
            journey=story;
            speed=(story.water&1)!=0 ? 27 : 0;
        }
        void Update()
        {
            float target=(journey.water&1)!=0 ? 27 : 0;
            speed=Mathf.MoveTowards(speed,target,Time.deltaTime*12);
            if(speed>0)transform.Rotate(localAxle,speed*Time.deltaTime,Space.Self);
        }
    }
}
