"""Fen's lock gauge and Ossa's glass furnace tools, built with the same figure scale as Moss."""
import math
from moss_art import Figure
from atelier import RES

def paint(atlas):
    import numpy as np
    from PIL import Image
    from scipy.ndimage import gaussian_filter
    colors={
        'FenAtelier':[(49,79,74),(69,116,110),(186,153,76),(181,126,90),(86,61,45),(49,64,65),
            (126,86,56),(162,137,102),(204,184,128),(142,74,52),(201,156,78),(57,45,38),
            (192,135,99),(55,73,83),(229,213,173),(126,75,61)],
        'OssaAtelier':[(103,67,61),(158,81,53),(77,89,99),(141,91,67),(81,54,46),(57,56,65),
            (63,44,44),(98,72,67),(207,177,130),(177,91,59),(193,148,80),(49,42,43),
            (161,107,77),(70,115,133),(228,203,156),(103,61,54)]}
    rng=np.random.default_rng(281 if atlas=='FenAtelier' else 932)
    image=np.zeros((128,128,3),np.uint8);yy,xx=np.mgrid[:32,:32]
    for i,c in enumerate(colors[atlas]):
        mott=gaussian_filter(rng.normal(size=(32,32)),1.8,mode='wrap');mott/=mott.std()
        brush=3*mott+rng.normal(0,1.5,(32,32))
        if i in (0,1,8):brush+=2*((xx+yy)%3-1)
        if i==13 and atlas=='OssaAtelier':brush+=12*np.cos((xx+yy*1.4)*math.pi/22)
        row,col=divmod(i,4)
        image[(3-row)*32:(4-row)*32,col*32:(col+1)*32]=np.uint8(np.clip(np.array(c)+brush[:,:,None],0,255))
    Image.fromarray(image).save(RES/'Textures'/(atlas+'.png'))

def maker(x,y,z,smith):
    f=Figure(x,y,z,'OssaAtelier' if smith else 'FenAtelier')
    rings,oval,tube,draw=f.rings,f.oval,f.tube,f.draw
    # Fen leans over a low gauge, while the glassblower stands taller with a bent tool arm.
    hip=.84 if smith else .80;waist=1.02 if smith else .96;shoulder=1.40 if smith else 1.29
    for s in [-1,1]:
        dx=s*(.133 if smith else .142);dy=s*(.03 if smith else .07)
        rings('Welted boot',[(dx,dy-.053,.006,.093,.162),(dx,dy-.053,.048,.112,.176),
              (dx,dy-.04,.097,.109,.169),(dx,dy,.20,.084,.10),(dx,dy,.28,.077,.082)],4,12)
        if smith:
            rings('Trouser leg',[(dx,dy,.20,.078,.089),(dx,dy,.32,.101,.103),(dx,dy-.028,.50,.115,.118),
                  (dx,dy,.61,.087,.100),(dx*.93,dy,.77,.123,.136),(dx*.81,.012,.89,.124,.133)],5)
            rings('Knitted gaiter',[(dx,dy,.19,.085,.099),(dx,dy,.22,.095,.103),(dx,dy,.33,.097,.095)],2)
        else:
            rings('High rubber wader',[(dx,dy,.125,.087,.113),(dx,dy,.24,.089,.099),
                  (dx,dy+.015,.42,.104,.112),(dx,dy-.012,.53,.118,.120),(dx,dy-.009,.57,.121,.116)],5)
            rings('Wader lip',[(dx,dy-.009,.535,.120,.118),(dx,dy-.009,.564,.128,.126),
                  (dx,dy-.009,.586,.122,.123)],0)
            rings('Gathered knee',[(dx,dy,.56,.109,.11),(dx,dy,.64,.129,.135),
                  (dx*.88,0,.76,.132,.146),(dx*.76,.013,.846,.143,.151)],13)
    if smith:
        rings('Linen work shirt',[(0,.02,.79,.21,.147),(0,.009,.88,.213,.152),(0,0,1.01,.177,.137),
              (0,0,1.23,.214,.175),(0,.015,1.37,.248,.164),(0,.016,1.425,.152,.124)],8)
        rings('Split kiln apron',[(.014,-.018,.54,.218,.154),(0,-.025,.61,.226,.164),(0,0,.83,.205,.164),
              (0,-.005,1.00,.185,.151),(0,-.046,1.20,.159,.145),(0,-.071,1.32,.14,.11)],1)
        for s in [-1,1]:
            tube('Apron strap',(s*.104,-.146,1.282),(s*.142,.009,1.411),.019,.023,4)
        rings('Apron tie',[(0,-.005,.958,.191,.157),(0,-.005,.998,.19,.156)],4)
        oval('Kiln apron pocket',(-.095,-.153,.853),(.074,.024,.082),0)
        tube('Shears handle',(-.11,-.166,.897),(-.132,-.171,.989),.015,.011,10)
    else:
        rings('Storm coat',[(0,.027,.70,.287,.184),(0,.01,.78,.281,.187),(.01,0,.96,.245,.176),
              (0,-.004,1.11,.263,.198),(0,.012,1.25,.267,.171),(-.01,.015,1.31,.133,.119)],1)
        rings('Tide keeper belt',[(.005,0,.913,.258,.185),(.005,0,.965,.249,.183)],4)
        oval('Lock fob',(-.033,-.182,.94),(.037,.015,.029),10)
        for q in [1.027,1.111,1.192]:
            oval('Horn toggle',(.012,-.187,q),(.023,.013,.012),8)
        rings('Folded storm hood',[(0,.015,1.17,.265,.178),(0,.036,1.235,.268,.192),
              (-.01,.045,1.308,.192,.149),(-.012,.031,1.342,.135,.122)],0)
    for s in [-1,1]:
        sh=(s*(.229 if smith else .252),.01,shoulder-.045)
        raised=s>0
        if raised:f.joint('SpeakerArm',sh)
        el=(s*(.328 if smith else .344),-.031,shoulder-.226)
        wrist=(s*(.219 if raised else .314),-.218 if raised else -.091,shoulder-(.222 if raised else .409))
        tube('Sleeve upper',sh,el,.107 if smith else .115,.080 if smith else .092,8 if smith else 1,10)
        tube('Rolled hem',el,(el[0],el[1]-.016,el[2]-.036),.097,.086,2,10)
        tube('Tool arm',el,wrist,.073,.049,3 if smith else 1,10)
        glove=2 if smith and not raised else 3
        oval('Working hand',wrist,(.066,.061,.076),glove)
        oval('Folded thumb',(wrist[0]-s*.049,wrist[1]-.021,wrist[2]+.016),(.03,.032,.045),glove)
        if raised and smith:
            tube('Glassworker’s blowing iron',(.199,-.245,1.02),(.30,-.23,1.51),.013,.012,13)
            oval('Gather of cooled glass',(.311,-.23,1.537),(.037,.035,.047),13)
        elif raised:
            tube('Gauge key stem',(.20,-.214,.956),(.253,-.219,1.216),.014,.014,10)
            tube('Square key bar',(.191,-.219,1.21),(.302,-.219,1.226),.017,.017,10)
        f.group='Speaker'
    face=1.63 if smith else 1.48
    f.joint('SpeakerHead',(0,0,face-.183))
    rings('Neck',[(0,.008,face-.236,.079,.077),(0,0,face-.102,.096,.096)],3)
    rings('Cheekbones and jaw',[(0,-.022,face-.168,.072,.075),(0,-.03,face-.136,.113,.118),
          (.004,-.019,face-.064,.148,.137),(0,-.004,face+.022,.159,.143),
          (0,.008,face+.089,.151,.134),(0,.014,face+.144,.117,.111),(0,.018,face+.168,.061,.060)],3,16)
    for s in [-1,1]:
        oval('Lobed ear',(s*.149,0,face-.026),(.039,.038,.055),3)
        oval('Dark temple',(s*.135,.036,face+.028),(.043,.067,.089),6)
        oval('Eye',(s*.062,-.133,face+.014),(.034,.014,.021),14)
        oval('Iris',(s*.062-.002,-.146,face+.015),(.015,.005,.019),11)
        oval('Eye light',(s*.062-.006,-.151,face+.022),(.0055,.0025,.005),14,8)
        tube('Brow',(s*.027,-.143,face+.053),(s*.101,-.128,face+.044),.012,.011,6,7)
    oval('Nose bridge',(.001,-.143,face-.034),(.031,.043,.051),12)
    tube('Lower lip',(-.048,-.148,face-.090),(.047,-.149,face-.086),.007,.005,15)
    if smith:
        oval('Tied curls',(0,.082,face+.082),(.166,.116,.12),6)
        for i in range(7):
            a=i*math.tau/7
            oval('Dark curl',(.104*math.cos(a),.10*math.sin(a)+.052,face+.145+.024*math.sin(2*a)),
                 (.072,.067,.067),6 if i%3 else 7)
        oval('High bun',(.039,.102,face+.205),(.093,.082,.092),6)
        rings('Goggle strap',[(0,.018,face+.077,.161,.142),(0,.018,face+.103,.163,.142)],4)
        for s in [-1,1]:
            oval('Bronze lens frame',(s*.069,-.117,face+.101),(.064,.026,.045),10)
            oval('Kiln glass',(s*.069,-.141,face+.101),(.051,.011,.032),13)
        tube('Lens bridge',(-.018,-.14,face+.098),(.018,-.14,face+.097),.009,.009,10)
        oval('Copper eardrop',(-.160,-.006,face-.082),(.019,.012,.033),10)
    else:
        rings('Lock keeper’s beard',[(0,-.025,face-.220,.039,.06),(.012,-.053,face-.188,.095,.085),
              (0,-.032,face-.141,.134,.132),(0,-.022,face-.094,.14,.124)],6)
        for s in [-1,1]:
            oval('Whiskers',(s*.04,-.15,face-.073),(.052,.018,.020),6)
        rings('Waxed sou’wester brim',[(0,.032,face+.051,.229,.222),(0,.019,face+.071,.237,.222),
              (0,-.019,face+.099,.155,.145)],2,16)
        rings('Storm crown',[(0,.01,face+.078,.163,.147),(-.012,.018,face+.128,.17,.149),
              (-.031,.047,face+.188,.133,.118),(-.06,.062,face+.221,.060,.060)],2)
        for s in [-1,1]:
            tube('Hat braid',(s*.155,-.015,face+.064),(s*.121,-.092,face-.109),.005,.004,4,6)
