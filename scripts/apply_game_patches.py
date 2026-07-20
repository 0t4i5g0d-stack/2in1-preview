from pathlib import Path

path = Path("index.html")
s = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    s = s.replace(old, new, 1)


# Star configuration and item placement.
if "starDuration:10" not in s:
    replace_once(
        "  mushSpd:70, foeSpd:55, nokSpd:45, shellSpeed:260, hipDropSpeed:780,\n  cols:10, rowsBase:20, expStep:4, expMax:3,",
        "  mushSpd:70, starSpd:95, foeSpd:55, nokSpd:45, shellSpeed:260, hipDropSpeed:780,\n  starDuration:10, starGrace:5, starExtraRows:8,\n  cols:10, rowsBase:20, expStep:4, expMax:3,",
        "star config",
    )

if 'col:58,row:GROUND-3,used:false,item:"star"' not in s:
    replace_once(
        '  L.blocks.push({col:58,row:GROUND-3,used:false,item:"mush"});',
        '  L.blocks.push({col:58,row:GROUND-3,used:false,item:"star"});',
        "second mushroom box to star",
    )

if "let starTimer=0" not in s:
    replace_once(
        "let L,P,A,timer,isBig,expandLevel,ents,floats,flash,elapsed,deaths,ships,hits,loseReason,anim=0;",
        "let L,P,A,timer,isBig,expandLevel,ents,floats,flash,elapsed,deaths,ships,hits,loseReason,anim=0;\nlet starTimer=0,starGraceTimer=0,starExtraRows=0;",
        "star state",
    )
    replace_once(
        "  L=buildLevel(); timer=CFG.timeStart; isBig=false; expandLevel=0;",
        "  L=buildLevel(); timer=CFG.timeStart; isBig=false; expandLevel=0; starTimer=0; starGraceTimer=0; starExtraRows=0;",
        "star reset",
    )

if "guard++<CFG.starExtraRows" not in s:
    replace_once(
        '  if(collide(P.cur,0,0,P.cur.rot)) gameOver("積みあがってゲームオーバー");',
        '''  let guard=0;
  while(collide(P.cur,0,0,P.cur.rot) && (starTimer>0||starGraceTimer>0) && guard++<CFG.starExtraRows){
    P.grid.unshift(emptyRow()); starExtraRows++; P.cur.row++;
  }
  if(collide(P.cur,0,0,P.cur.rot)) gameOver("積みあがってゲームオーバー");''',
        "star top-out suspension",
    )

if "starTimer>0||A.invuln>0" not in s:
    replace_once(
        "function applyDamage(){ if(A.invuln>0)return;",
        "function applyDamage(){ if(starTimer>0||A.invuln>0)return;",
        "star invulnerability",
    )

if "function activateStar()" not in s:
    anchor = 'function addFloat(text,x,y,color,toTimer){ floats.push({text,x,y,color,life:1.0,vy:-24,toTimer:!!toTimer}); }'
    star_functions = '''function addFloat(text,x,y,color,toTimer){ floats.push({text,x,y,color,life:1.0,vy:-24,toTimer:!!toTimer}); }
function activateStar(){
  if(starExtraRows===0){
    starExtraRows=CFG.starExtraRows;
    for(let i=0;i<starExtraRows;i++) P.grid.unshift(emptyRow());
    if(P.cur) P.cur.row+=starExtraRows;
  }
  starTimer=CFG.starDuration;
  starGraceTimer=0;
  addFloat("STAR "+CFG.starDuration+"s",PX+PWD*0.5,PYY+PVH*0.30,"#fff176");
}
function starOverflowClear(){
  if(starExtraRows<=0) return true;
  const lockedClear=P.grid.slice(0,starExtraRows).every(row=>row.every(v=>!v));
  const activeClear=!P.cur||pieceCells(P.cur,P.cur.rot).every(([,r])=>r>=starExtraRows);
  return lockedClear&&activeClear;
}
function finishStarOverflow(){
  if(starExtraRows<=0) return;
  if(!starOverflowClear()){ gameOver("スター終了：枠外にブロック"); return; }
  P.grid.splice(0,starExtraRows);
  if(P.cur) P.cur.row-=starExtraRows;
  starExtraRows=0;
  starGraceTimer=0;
  addFloat("SAFE",PX+PWD*0.5,PYY+PVH*0.30,"#38d038");
}
function updateStar(dt){
  if(starTimer>0){
    starTimer=Math.max(0,starTimer-dt);
    if(starTimer===0){
      starGraceTimer=CFG.starGrace;
      addFloat("枠内へ "+CFG.starGrace+"s",PX+PWD*0.5,PYY+PVH*0.30,"#f83c3c");
    }
  }else if(starGraceTimer>0){
    if(starOverflowClear()){ finishStarOverflow(); return; }
    starGraceTimer=Math.max(0,starGraceTimer-dt);
    if(starGraceTimer===0) finishStarOverflow();
  }
}'''
    replace_once(anchor, star_functions, "star functions")

# Add star spawning to the existing item release function.
if 'b.item==="star"' not in s:
    start = s.index("function releaseBlockItem(b,q){")
    end = s.index("function resolveBlocks(){", start)
    s = s[:start] + '''function releaseBlockItem(b,q){
  if(b.used||!b.item) return;
  b.used=true;
  if(b.item==="mush") ents.push({type:"mush",x:q.cx,y:q.y,vy:-160,dir:1,alive:true,anim:0});
  else if(b.item==="coin") ents.push({type:"coin",x:q.cx,y:q.y,vy:-260,dir:0,alive:true,anim:0});
  else if(b.item==="star") ents.push({type:"star",x:q.cx,y:q.y,vy:-300,dir:1,alive:true,anim:0});
}
''' + s[end:]

if 'e.type==="star"?CFG.starSpd' not in s:
    replace_once(
        '    const spd = e.type==="coin"?0 : e.type==="mush"?CFG.mushSpd : e.type==="foe"?CFG.foeSpd :',
        '    const spd = e.type==="coin"?0 : e.type==="star"?CFG.starSpd : e.type==="mush"?CFG.mushSpd : e.type==="foe"?CFG.foeSpd :',
        "star movement",
    )

if 'e.vy=e.type==="star"?-300:0' not in s:
    replace_once(
        '    if(gy!==null && prevY<=gy && e.y>=gy && e.vy>=0){ e.y=gy; e.vy=0; }',
        '    if(gy!==null && prevY<=gy && e.y>=gy && e.vy>=0){ e.y=gy; e.vy=e.type==="star"?-300:0; }',
        "star bounce",
    )

if 'else if(e.type==="star"){ activateStar();' not in s:
    replace_once(
        '      else if(e.type==="coin"){ P.nextGold=true; e.alive=false; addFloat("GOLD NEXT",PX+PWD*0.5,PYY+PVH*0.3,GOLD); }\n      else if(e.type==="foe"){',
        '      else if(e.type==="coin"){ P.nextGold=true; e.alive=false; addFloat("GOLD NEXT",PX+PWD*0.5,PYY+PVH*0.3,GOLD); }\n      else if(e.type==="star"){ activateStar(); e.alive=false; }\n      else if(e.type==="foe"){',
        "star collection",
    )

if 'addFloat("STAR撃破"' not in s:
    replace_once(
        '''      else if(e.type==="foe"){
        if(stomp){ e.alive=false; A.vy=-CFG.stompBounce; } else applyDamage();
      } else if(e.type==="nok"){
        if(e.state==="walk"){''',
        '''      else if(e.type==="foe"){
        if(starTimer>0){ e.alive=false; addFloat("STAR撃破",AX+AW*0.5,AY+44,"#fff176"); }
        else if(stomp){ e.alive=false; A.vy=-CFG.stompBounce; } else applyDamage();
      } else if(e.type==="nok"){
        if(starTimer>0){ e.alive=false; addFloat("STAR撃破",AX+AW*0.5,AY+44,"#fff176"); }
        else if(e.state==="walk"){''',
        "star contact defeat",
    )

if "updateStar(STEP)" not in s:
    replace_once(
        "      updateAction(STEP,frame); updateEntities(STEP); updatePuzzle(STEP,frame);",
        "      updateAction(STEP,frame); updateEntities(STEP); updatePuzzle(STEP,frame); updateStar(STEP);",
        "star timer loop",
    )

# Drawing helpers for star and gold blocks.
if "function drawGoldBlock" not in s:
    anchor = "function brick(x,y,s){"
    helpers = '''function drawGoldBlock(x,y,s,phase=0){
  const pulse=0.5+0.5*Math.sin(anim*5+phase*0.17);
  block3d(x,y,s,"hsl(46 100% "+(52+Math.round(pulse*11))+"%)");
  g.save(); g.beginPath(); g.rect(x+1,y+1,s-2,s-2); g.clip();
  const sweep=((anim*0.9+phase*0.071)%1.6)-0.3;
  g.translate(x+sweep*s,y+s*0.5); g.rotate(-Math.PI/4);
  g.globalAlpha=0.22+0.34*pulse; g.fillStyle="#fff"; g.fillRect(-s*0.09,-s,s*0.18,s*2);
  g.restore();
  const twinkle=0.5+0.5*Math.sin(anim*8+phase*1.7);
  if(twinkle>0.70){
    const a=(twinkle-0.70)/0.30, sx=x+s*0.78, sy=y+s*0.20, r=s*(0.07+0.09*a);
    g.save(); g.globalAlpha=0.45+0.55*a; g.strokeStyle="#fff"; g.lineWidth=Math.max(1,s*0.045);
    g.beginPath(); g.moveTo(sx-r,sy); g.lineTo(sx+r,sy); g.moveTo(sx,sy-r); g.lineTo(sx,sy+r); g.stroke(); g.restore();
  }
}
function brick(x,y,s){'''
    replace_once(anchor, helpers, "gold drawing helper")

if "function traceStar(" not in s:
    anchor = "function drawFoe(x,yfoot,t){"
    helpers = '''function traceStar(r){
  g.beginPath();
  for(let i=0;i<10;i++){
    const a=-Math.PI/2+i*Math.PI/5, rr=i%2===0?r:r*0.46;
    const x=Math.cos(a)*rr, y=Math.sin(a)*rr;
    if(i===0) g.moveTo(x,y); else g.lineTo(x,y);
  }
  g.closePath();
}
function drawStarItem(x,yfoot,t){
  const r=TILE*0.38;
  g.save(); g.translate(x,yfoot-r*1.05); g.rotate(Math.sin(t*5)*0.18);
  g.shadowColor="#fff176"; g.shadowBlur=10;
  g.fillStyle="hsl("+((t*180)%360)+" 95% 62%)"; traceStar(r); g.fill();
  g.shadowBlur=0; g.strokeStyle="#fff"; g.lineWidth=2; g.stroke();
  g.fillStyle="#111"; g.fillRect(-r*0.32,-r*0.15,r*0.13,r*0.24); g.fillRect(r*0.19,-r*0.15,r*0.13,r*0.24);
  g.restore();
}
function drawStarAura(x,y,w,h){
  g.save();
  g.globalAlpha=0.24; g.fillStyle="hsl("+((anim*220)%360)+" 100% 65%)";
  g.beginPath(); g.ellipse(x,y-h*0.5,w*0.9,h*0.7,0,0,Math.PI*2); g.fill();
  g.globalAlpha=0.9; g.fillStyle="#fff";
  for(let i=0;i<3;i++){
    const a=anim*3+i*2.1, sx=x+Math.cos(a)*w*0.8, sy=y-h*0.5+Math.sin(a)*h*0.55;
    g.fillRect(sx-1,sy-4,2,8); g.fillRect(sx-4,sy-1,8,2);
  }
  g.restore();
}
function drawFoe(x,yfoot,t){'''
    replace_once(anchor, helpers, "star drawing helpers")

if 'else if(e.type==="star") drawStarItem' not in s:
    replace_once(
        '    else if(e.type==="coin") drawCoin(e.x,e.y,e.anim);\n    else if(e.type==="foe")',
        '    else if(e.type==="coin") drawCoin(e.x,e.y,e.anim);\n    else if(e.type==="star") drawStarItem(e.x,e.y,e.anim);\n    else if(e.type==="foe")',
        "render star item",
    )

if "drawStarAura(A.x" not in s:
    replace_once(
        "  if(!(A.invuln>0 && Math.floor(A.invuln*12)%2===0)) drawHero(A.x-A.w/2,A.y-A.h,A.w,A.h,A.face,A.crouch);",
        "  if(starTimer>0) drawStarAura(A.x,A.y,A.w,A.h);\n  if(!(A.invuln>0 && Math.floor(A.invuln*12)%2===0)) drawHero(A.x-A.w/2,A.y-A.h,A.w,A.h,A.face,A.crouch);",
        "render star aura",
    )

# Replace the puzzle renderer with a rule panel, gold animation, and overflow display.
if "function renderRulePanel(" not in s:
    start = s.index("function renderPuzzle(){")
    end = s.index("function renderEcho(){", start)
    replacement = '''function renderRulePanel(x,y,w,h){
  const fs=Math.max(7,Math.min(11,Math.floor(w/12),Math.floor(h/25)));
  const gap=fs*1.38;
  const lines=[
    ["RULE","#fff"],
    ["固定 +1秒","#aaa"],
    ["1/2/3/4 LINE","#fff"],
    ["+5/+10/+15/+20秒","#f8d800"],
    ["COIN → 次がGOLD",GOLD],
    ["GOLD LINE ×2",GOLD],
    ["STAR 10秒","#fff176"],
    ["SIDE 接触で敵撃破","#5c94fc"],
    ["STACK 枠外OK","#f8d800"],
    ["終了後5秒で枠内へ","#f83c3c"],
    ["HIP 箱/レンガ破壊","#aaa"]
  ];
  let yy=y;
  if(starTimer>0) lines.unshift(["★ "+starTimer.toFixed(1)+"秒","#fff176"]);
  else if(starGraceTimer>0) lines.unshift(["RETURN "+starGraceTimer.toFixed(1)+"秒","#f83c3c"]);
  g.textAlign="left"; g.textBaseline="top"; g.font="700 "+fs+"px 'Courier New',monospace";
  for(const [text,color] of lines){
    if(yy+fs>y+h) break;
    g.fillStyle=color; g.fillText(text,x,yy); yy+=gap;
  }
  g.textBaseline="alphabetic";
}
function renderPuzzle(){
  g.save(); g.beginPath(); g.rect(PX,PYY,PWD,PVH); g.clip();
  g.fillStyle="#101010"; g.fillRect(PX,PYY,PWD,PVH);
  const R=rows(), panelW=Math.max(82,Math.min(154,PWD*0.31)), gap=8;
  const boardAreaW=Math.max(PW*6,PWD-panelW-gap-8);
  const cell=Math.max(6,Math.floor(Math.min(boardAreaW/PW,PVH/R)));
  const boardW=PW*cell, boardH=R*cell;
  const ox=PX+4+Math.max(0,(boardAreaW-boardW)/2), oy=PYY+(PVH-boardH)/2;
  const panelX=ox+boardW+gap, panelRight=PX+PWD-4, actualPanelW=Math.max(60,panelRight-panelX);
  g.fillStyle="#000"; g.fillRect(ox-3,oy-3,boardW+6,boardH+6);
  const overflowRows=Math.min(starExtraRows,R);
  for(let r=0;r<R;r++)for(let c=0;c<PW;c++){
    const x=ox+c*cell,y=oy+r*cell;
    g.fillStyle=r<overflowRows?(starTimer>0?"rgba(255,215,0,.18)":"rgba(248,60,60,.16)"):"#181818";
    g.fillRect(x,y,cell,cell); g.strokeStyle="#242424"; g.lineWidth=1; g.strokeRect(x+.5,y+.5,cell-1,cell-1);
    const v=P.grid[r][c];
    if(v){ if(v===GOLD) drawGoldBlock(x,y,cell,r*PW+c); else block3d(x,y,cell,v); }
  }
  if(overflowRows>0){
    const by=oy+overflowRows*cell;
    g.strokeStyle=starTimer>0?"#fff176":"#f83c3c"; g.lineWidth=3;
    g.beginPath(); g.moveTo(ox,by); g.lineTo(ox+boardW,by); g.stroke();
  }
  if(P.cur){
    for(const [c,r] of pieceCells(P.cur,P.cur.rot)){
      if(r<0)continue;
      const x=ox+c*cell,y=oy+r*cell;
      if(P.cur.gold) drawGoldBlock(x,y,cell,700+c+r*PW); else block3d(x,y,cell,PCOL[P.cur.t]);
    }
  }
  if(expandLevel>0){
    const added=Math.min(R,starExtraRows+expandLevel*CFG.expStep), by=oy+added*cell;
    g.strokeStyle="#38d038"; g.lineWidth=2; g.beginPath(); g.moveTo(ox,by); g.lineTo(ox+boardW,by); g.stroke();
  }
  g.fillStyle="#fff"; g.font="700 11px 'Courier New',monospace"; g.textAlign="left"; g.fillText("NEXT",panelX,PYY+14);
  if(P.next){
    const ps=Math.max(6,Math.min(14,cell*0.65));
    for(const [c,r] of SHAPES[P.next][0]){
      const x=panelX+c*ps,y=PYY+20+r*ps;
      if(P.nextGold) drawGoldBlock(x,y,ps-1,900+c+r*4); else block3d(x,y,ps-1,PCOL[P.next]);
    }
  }
  renderRulePanel(panelX,PYY+70,actualPanelW,PVH-74);
  g.restore();
  g.strokeStyle="#000"; g.lineWidth=2; g.strokeRect(PX+1,PYY,PWD-2,PVH);
  g.textAlign="center";
  for(const fl of floats){ g.globalAlpha=Math.max(0,fl.life);
    g.fillStyle=fl.color; g.font="700 15px 'Courier New',monospace"; let fx=fl.x,fy=fl.y;
    if(fl.toTimer){ const t=1-fl.life; fx=fl.x+(W/2-fl.x)*t*t; fy=fl.y+((TBy+14)-fl.y)*t*t; }
    g.fillText(fl.text,fx,fy); }
  g.globalAlpha=1;
}
'''
    s = s[:start] + replacement + s[end:]

path.write_text(s, encoding="utf-8")
