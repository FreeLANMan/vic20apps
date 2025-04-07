10 rem *** space dodger ***
20 rem *** a game for the vic-20 ***
30 poke 36879,8: rem set screen color
40 print chr$(147): rem clear screen
50 print "*** space dodger ***"
60 print "avoid the asteroids!"
70 print "use a,s keys to move"
80 print "press any key to start"
90 get k$: if k$="" then 90
100 print chr$(147): rem clear screen

110 rem *** initialize variables ***
120 sc=0: rem score
130 px=10: rem player x position
140 py=22: rem player y position
150 sp=100: rem game speed
160 dim ax(5): rem asteroid x positions
170 dim ay(5): rem asteroid y positions
180 for i=1 to 5
190   ax(i)=int(rnd(1)*20)+1
200   ay(i)=int(rnd(1)*10)+1
210 next i

220 rem *** main game loop ***
230 print chr$(147)
240 poke 36879,8

250 rem *** draw player ***
260 poke 7680+py*22+px,81: rem player character

270 rem *** draw asteroids ***
280 for i=1 to 5
290   poke 7680+ay(i)*22+ax(i),42: rem asteroid character
300 next i

310 rem *** display score ***
320 poke 7680,19: poke 7681,3: rem 'sc'
330 poke 7682,58: rem ':'
340 s$=str$(sc)
345 if left$(s$,1)=" " then s$=right$(s$,len(s$)-1)
350 for i=1 to len(s$)
355   c=asc(mid$(s$,i,1))
360   poke 7682+i,c
370 next i

380 rem *** check keyboard ***
390 get k$
400 if k$="a" and px>0 then px=px-1
410 if k$="s" and px<21 then px=px+1

420 rem *** move asteroids ***
430 for i=1 to 5
440   ay(i)=ay(i)+1
450   if ay(i)<=22 then 500
460   ay(i)=1
470   ax(i)=int(rnd(1)*20)+1
480   sc=sc+1
500 next i

510 rem *** check collision ***
520 for i=1 to 5
530   if ax(i)=px and ay(i)=py then goto 600
540 next i

550 rem *** delay ***
560 for d=1 to sp: next d

570 goto 230: rem return to main loop

600 rem *** game over ***
610 print chr$(147)
620 print "game over!"
630 print "your score: ";sc
640 print "play again? (y/n)"
650 get r$: if r$="" then 650
660 if r$="y" then run
670 end

