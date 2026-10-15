#!/usr/bin/env python3
""" change a csv export from spotify to work with splitaudio. file should be in same directory
Usage:
    python convertspotifycsv.py
    uses [ProjectName] playlist.wav/.csv TODO take these as input
    fetches files from MusicDir/[ProjectName]/Input
"""

import os
import sys
import datetime
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
MusicDir = "/mnt/c/Users/Lucas/Music/Spotify2CD/"
ProjectName = "Sterre"

inputdir= f"{MusicDir}{ProjectName}/Input/"
inputcsvdir= f"{MusicDir}{ProjectName}/Input/"
outputdir= f"{MusicDir}{ProjectName}/Output/"
input= ProjectName + """ playlist.wav"""
inputcsv= ProjectName + """ playlist.csv"""
command = f"splitaudio -i '{inputdir}{input}' -c output.csv -o {outputdir}"

def run(cmd, check=True, cwd=None):
    """Run a shell command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=cwd or REPO_ROOT
    )
    if check and result.returncode != 0:
        print(f"  Command failed: {cmd}")
        if result.stderr:
            print(f"  stderr: {result.stderr.strip()}")
    return result.returncode, result.stdout.strip(), result.stderr.strip()
    
def formattimercount(timercount):
    hours = int(timercount.seconds/3600)
    minutes = int(timercount.seconds/60) - hours*60
    seconds = int(timercount.seconds - minutes*60 - hours*3600)
    result = f"{hours}:{minutes}:{seconds}"
    #print(result)
    return result
    
def main():    
    #open and read the file:
    print(f"starting convertion of {input} into multiple")
    with open(f"{inputcsvdir}{inputcsv}") as inputfile: 
      content =""
      count =0
      timercount = datetime.timedelta(days=0, seconds=0, minutes=0, hours=0, weeks=0)
      nexttimercount = timercount
      for line in inputfile.readlines():
          count+=1          
          updatedline = line
          if count == 1:
              updatedline = "artist,title,position\n"
          else:
              indexlastcomma = updatedline.rindex(",")+2
              durationstring = updatedline[indexlastcomma::].strip()
              #print(f" reading time: {durationstring}")
              nexttimercount += datetime.timedelta(weeks=0,days=0,hours=int(durationstring.split(":")[0]),minutes=int(durationstring.split(":")[1]),seconds=int(durationstring.split(":")[2]))
              nexttimercount += datetime.timedelta(milliseconds=850)
              updatedline = updatedline[:indexlastcomma:]+formattimercount(timercount)+'\n'
              timercount = nexttimercount
          content += updatedline

    output = REPO_ROOT / "output.csv"
    new_csv = content
    open(output, "w").write(new_csv)    
    responcecode, output, err = run(f"{command} -d")
    print(output)

if __name__ == "__main__":
    main()

