from pathlib import Path
p=Path(__file__).resolve().parent
c=p.parent/'03_the_crack'/'src'
s=(c/'build_crack.py').read_text(encoding='utf-8-sig')
s=s.replace("""    arm.matrix_world=Matrix.Translation(Vector((.357 if pass_number>=3 else (.355 if pass_number==2 else .22),.673,-.157 if pass_number>=3 else -.020)))@Matrix.Rotation(math.radians(166),4,'Z')
    settle=ctx['ease'](f,9,64)""","""    discover=ctx['ease'](f,14,34)
    turn=ctx['ease'](f,36,67)
    recoil=discover*(1-ctx['ease'](f,29,51))
    arm.matrix_world=Matrix.Translation(Vector((.357-.037*turn,.673-.028*recoil,-.157+.034*recoil)))@Matrix.Rotation(math.radians(166-91*turn),4,'Z')
    settle=ctx['ease'](f,9,64)""",1)
s=s.replace("""    orient_rest(bones['J_Bip_C_Chest'],(0,0,1),math.radians(-4+5*settle))
    orient_rest(bones['J_Bip_C_Neck'],(1,0,0),math.radians(-9-14*settle))
    orient_rest(bones['J_Bip_C_Head'],(0,0,1),math.radians(-5+10*settle))""","""    orient_rest(bones['J_Bip_C_Chest'],(0,0,1),math.radians(-4+5*settle-13*turn))
    orient_rest(bones['J_Bip_C_Neck'],(1,0,0),math.radians(-7-11*discover+22*turn))
    orient_rest(bones['J_Bip_C_Head'],(0,0,1),math.radians(-5-26*turn))
    for obj in ctx['sam']:
        shapes=obj.data.shape_keys if obj.type=='MESH' else None
        if shapes:
            for name,value in (('Fcl_EYE_Close',.84*math.exp(-((f-49)/2.8)**2)),('Fcl_BRW_Sorrow',.48*discover)):
                block=shapes.key_blocks.get(name)
                if block:
                    block.value=value""",1)
s=s.replace("if run_frames=='all' else","if run_frames in ('all','resume') else")
s=s.replace("""    sc.render.filepath=str(OUT/f'cel_{f:03d}.png')
    bpy.ops.render.render(write_still=True)""","""    path=OUT/f'cel_{f:03d}.png'
    if run_frames!='resume' or not path.exists():
        sc.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)""")
compile(s,str(c/'build_crack_v6.py'),'exec')
(c/'build_crack_v6.py').write_text(s,encoding='utf-8')
f=p/'run_shot.ps1'
s=f.read_text(encoding='utf-8-sig')
s=s.replace("$card=$plan[$Shot]\n","""$card=$plan[$Shot]
$crackV6=$Shot -eq '03' -and $env:KOBAN_PICTURE_REVISION -eq '6'
if($crackV6){$card=@{slug='the_crack';scene='crack';frames=96;keys=@(1,29,46,63,74,96);stills=@(1,33,67,96)}}
""",1)
needle='    $render=Start-Process -FilePath $Blender'
i=s.index(needle)
s=s[:i]+"""    if($crackV6){
        $shotScript=Join-Path $dest 'src/build_crack_v6.py'
        $launchArgs=@('-b','-t','6','--factory-startup','--python-exit-code','1','-P',"`"$shotScript`"",'--',"`"$cel`"",$scale,$keys,'4')
    }
"""+s[i:]
s=s.replace("""python (Join-Path $PSScriptRoot 'finish_frames.py') $cel $framesOut $Shot""","""if($crackV6){
    python (Join-Path $dest 'src/comp_crack.py') $cel $framesOut 4
}else{
    python (Join-Path $PSScriptRoot 'finish_frames.py') $cel $framesOut $Shot
}""",1)
s=s.replace('    @" \nShared scene source: ../production/$($card.scene).py','''    $sourceName=if($env:KOBAN_PICTURE_REVISION -eq '6'){"SOURCE_v$Version.md"}else{'SOURCE.md'}
    $recipe=if($crackV6){'build_crack_v6.py'}elseif($env:KOBAN_PICTURE_REVISION -eq '6'){"../production/$($card.scene)_v6.py"}else{"../production/$($card.scene).py"}
    @" 
Shared scene source: $recipe''',1)
s=s.replace("Join-Path $dest 'src/SOURCE.md'","Join-Path $dest \"src/$sourceName\"")
f.write_text(s,encoding='utf-8')
