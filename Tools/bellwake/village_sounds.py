"""Short original field recordings synthesized for the market and the provisions counter."""
from pathlib import Path
import subprocess
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io.wavfile import write
from tempfile import TemporaryDirectory

out=Path(__file__).resolve().parents[2]/'Assets/Resources/Bellwake/Audio'
rate=24000
rng=np.random.default_rng(518)
def seconds(n):
    return np.arange(round(n*rate))/rate
def envelope(t,attack,release):
    return np.minimum(1,t/attack)*np.minimum(1,np.maximum(0,t[-1]-t)/release)
def band(t,low,high):
    return sosfilt(butter(3,(low,high),btype='bandpass',fs=rate,output='sos'),rng.normal(size=len(t)))
def save(name,wave):
    with TemporaryDirectory() as temp:
        path=Path(temp)/'take.wav'
        write(path,rate,np.int16(32767*wave/max(.001,np.max(np.abs(wave)))*.77))
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(path),
                        '-map_metadata','-1','-c:a','libvorbis','-q:a','4',str(out/(name+'.ogg'))],check=True)

hen=np.zeros(len(seconds(.95)))
for delay,pitch,duration,power in [(.03,450,.18,.55),(.28,575,.11,.38),(.44,640,.26,1)]:
    t=seconds(duration)
    sweep=pitch*(1.45-.87*t/duration)+18*np.sin(27*t)
    phase=2*np.pi*np.cumsum(sweep)/rate
    call=(np.sin(phase)+.46*np.sin(2*phase)+.23*np.sin(3*phase)+.45*band(t,670,2000))
    start=round(delay*rate);hen[start:start+len(t)]+=call*envelope(t,.012,.08)*np.exp(-t*6)*power
save('YardHen',hen)

t=seconds(1.12)
drag=band(t,190,720)*(.65+.2*np.sin(2*np.pi*(19*t+6*t*t)))
groan=np.sin(2*np.pi*(116*t+33*t*t)+.6*np.sin(35*t))
save('MillBearing',(drag*.62+groan*.30)*envelope(t,.24,.43)*np.sin(np.pi*t/t[-1])**2)

t=seconds(8)
night=np.zeros_like(t)
for offset,base in [(0.17,3115),(1.16,3505),(3.93,2985),(6.15,3320)]:
    for j in range(3):
        ts=seconds(.12+j*.014);start=round((offset+j*.27)*rate)
        pulse=(.5+.5*np.sin(2*np.pi*42*ts))**3
        voice=np.sin(2*np.pi*(base*ts+22*ts**2))*pulse*envelope(ts,.022,.04)
        night[start:start+len(ts)]+=voice*(.58+j*.07)
save('YardDusk',night)

chime=np.zeros(len(seconds(1.37)))
for onset,freq,power in [(0,392,.76),(.10,523.25,.80),(.26,659.25,.82),(.39,587.33,.55)]:
    t=seconds(.88);phase=2*np.pi*t*freq
    wave=(np.sin(phase)*np.exp(-4*t)+.32*np.sin(2.01*phase)*np.exp(-11*t)+.10*np.sin(3.96*phase)*np.exp(-19*t))
    start=round(onset*rate);chime[start:start+len(t)]+=wave*envelope(t,.005,.13)*power
save('FareChime',chime)
