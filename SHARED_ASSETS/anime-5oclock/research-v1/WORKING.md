# WORKING.md : everything so far (handoff log)

Written 2026-11-22. Project: Sam's money automation at peek, anime / Night Terror / "5 O'CLOCK" branch. This file is the memory. Update it as you work.

Codex follow-up, 2026-11-22. [REEL_RESEARCH.md](REEL_RESEARCH.md) contains the live comment review, public counts, runtime checks, Japanese and cross-platform comparisons, and a test brief. The road reel has 398K views. A same-creator reel of nearly identical length has 34.4M. Numbered logs are a format worth testing. Public views and current followers cannot tell us whether numbering, watch time, or an app funnel converted viewers. The local `story/` folder was still absent.

## 0. What Sam asked (in his own words, shortened)
1. He shared a reel (Granite Waves) and said the animation is 2D, not 3D, and "looks so damn good". Wanted: what art form it is, the channel and its other reels, how the creator makes them.
2. He loved the voice and asked for a very deep analysis of it, to reproduce for our dialogue.
3. He said: we are not copying anything. We take inspiration from the art form (purely anime style). Our own characters, scenes and story. A unique story comes first, before characters. He likes Chainsaw Man, Pacific Rim, Kaiju No. 8. Setting: a Japanese place, Sam is the main character. A "fabulous and crazy" plot that can have millions of reels around it. Wanted 5 story ideas.
4. He shared a second reel (night road with a black void). He said it feels like an alternate universe communicating with Earth, and that "we are going to revolve around this idea", one concept that people engage with a lot. He wants a lot of research first: what viewers see, what is missing, what should be there so people are amazed. "Use the web at the fullest, use the Insta at the fullest."
5. He wants everything tracked in this folder so it can continue in Codex (tokens are low; reset after about 1 hour).

## 1. Story concept in play (from the story thread, not by me)
"5 O'CLOCK": a Japanese town, lone survivor (Sam), a loudspeaker song at 5 PM answered by another Earth, kaiju, rules, suspense. The story files are written by the thread "Pitch 5 anime story ideas" and are copied into `story/` here when ready. Check there first.

## 2. Reel 1: Granite Waves (art form)
- It is hand-drawn 2D anime in a vertical (9:16) "micro-drama" series. Flat cel colour, thin dark line, muted palette with one accent colour (red jacket), soft heavily blurred painted backgrounds, long held poses, tiny movements (eyelids, hair, breath), burned-in subtitles in the lower third, Matt Lange "Punish Me" used as music on other reels.
- Channel: granitewavesseries 1.2M followers, 98 posts. Creator Tezeze (tezeze_art, 630K). Streaming only on the Ryuu app, which funded season 1. Top reel 58.5M views. Highlights: Start here, Pilot, Zima, #dtiys 100K, Elya, VA tutorial, VAs.
- Making-of: a "Final vs animatic" BTS reel shows a rough pencil animatic beside the finished frame. Tool names are NOT confirmed (no making-of found, web search found nothing). Likely: storyboard, pencil animatic, digital inking, flat fills with one shadow layer, painted/blurred background, compositing grade. Frame rate not measured (likely 12 to 24 fps with holds).
- Full doc: `granite-waves-study.html` (also published as an Artifact: https://claude.ai/artifact/YYZsuSf6ZoRv7igTrz2iZD).

## 3. Reel 1 voice analysis
I cannot listen. I measured the audio in the browser (pitch, loudness, spectrum) while the reel played. Music is mixed in, so numbers are approximate.
- Pitch about 70 to 105 Hz, mostly 80 to 95 Hz (low male voice).
- 60 to 90 percent of the energy below 250 Hz, spectral centre 200 to 450 Hz, almost nothing above 6 kHz: very warm and dark, close mic, rolled-off highs.
- Line peaks RMS 0.17 to 0.29, tails fall to 0.02 to 0.06: starts with weight, then fades. Tired, weary delivery.
- Pacing: lines of 1.5 to 3 s, gaps 1 to 3 s. Silence is part of the acting.
- No audible room echo (dry booth).
- Real human actors almost certainly: the channel credits named pro VA Sarah Natochenny on Ep 2, has "VAs" and "VA tutorial" highlights, and a sibling series credits a VA and a sound designer.
- Recipe for us: cast a real person with a low tired close-mic voice, speak quietly with weight at the start of lines and fade, leave a second of silence between lines. Record about 10 cm from the mic with a pop filter in a quiet small room. Mix: cut under 70 Hz, lift 150 to 250 Hz, roll off above 6 to 8 kHz, light compression, no reverb, duck music 8 to 10 dB under lines.
- Sam wants nothing that sounds AI-made, so use a real voice.

## 4. Reel 1 verdict for Night Terror
- Reproducible in Blender with Grease Pencil: flat cel fills, thin line, blurred background layer via compositor defocus, one accent colour per scene, cold colour grade, big bold subtitles.
- Needs hand-drawn key poses and long holds (animate on twos, small moves) so it does not look generated.
- Do not copy characters, logo or titles. Technique only.
- Next step suggested: one test shot (character in profile, held pose, blurred window, one red accent, real voice line), compare against `frames/f1_risk.jpg`.

## 5. Reel 2: "起秋" by @pseudohuasca
- 13.7 s, 1080x1920. One continuous locked shot of an empty night road (Taiwan-style: red curb line, double yellow centre line, streetlights, trees). No dialogue, no on-screen text.
- Beat map (approx., from frames at 20/40/60/80/100 percent): empty road, then a thin dark figure far down the road at the bend (about 20 percent), then a black diamond-shaped void with fragmented jittery edges and dark shards on the asphalt (about 60 percent), then the void fills about a third of the frame and eats the road (about 80 to 100 percent).
- Suspense method: ordinary footage first so every change feels wrong, tiny far thing so you lean in, slow escalation in one place, warm lights vs pure black (missing reality), no explanation, no cut away.
- Sound: could not be measured (audio reader returned silence). Caption credits Ableton for sound design, so a designed drone or glitch bed is likely.
- Made with: Ableton, TouchDesigner, After Effects, Blender (credited in caption).
- Story use: another reality leaking in as one small wrongness in a normal place. Frames: `frames/r1` to `r4`.

## 6. Instagram research (so far, read only)
Method: hashtag pages (only hashtags work; text keyword searches return nothing), account profile reels tabs (they show view counts), reel pages (caption, likes, comments).

Findings:
- Numbered-entry horror is the strongest serial format found. slumberspeak (156K followers, only 298 posts, captions say "Original Work - no Ai" and "Human made - no generative AI used") posts 8 s reels titled "entity 999000111 logged" and "Quest Log: 333 (with coordinates)". One reel got 4.9M views, others 996K and 473K, while typical posts get 4K to 20K. Spiky: the hit is a tiny, numbered, repeatable "log" format over looped real nature footage with a glowing glitchy entity. Also credits tools openly (After Effects, TouchDesigner, Ableton, Illustrator) and says no AI. Open credit builds trust.
- Animated horror novel format: toonimated (217K followers, 795 posts) posts black-and-white manga-style panels with burned-in subtitles that read like a novel being narrated; grid views 2.1M, 87K, 61K, 41K, 23K. "Metamortis" caption: psychological horror with metaphysical mystery, "a world whose rules defy understanding". It funnels to a YouTube channel (link in bio).
- Serial teasers from small accounts: dreadful_tree "You have been selected. Participation in the spiritual assessment is expected. Further instructions will follow. EPISODE 01 COMING SOON." (only 268 likes: a teaser with no proof of a world gets little).
- Candle Cove style retellings (horrorwithaura, 3.5K likes) show reused creepypasta underperforms. Original lore does better.
- Dreamcore / liminal tags are full of generic aesthetic posts, many AI-labelled (for example liminalhabitats tagging an AI tool, liminalsp3ces tagged "AI content"). Comments are things like "I like this side of instagram", "plz do not wake me", "your work is so good, very unsettling". Viewers want a feeling, not a story, and the generic pool is saturated. A real story with rules is a gap.
- Granite Waves shows the anime route: 58.5M on the season welcome reel, series tagged with episode numbers, funded by a streaming app, each reel is a clip from an episode with one emotional line burned in as subtitle.

Gaps still open for the next researcher (Codex or Claude):
- Comment themes on the biggest reels (comments did not load in my reads). Open each reel in Chrome, scroll the comments, note repeated asks like "part 2", "what is this", "I need the full story".
- Retention patterns: first-second hook, loop endings, "Part N" numbering, pinned comments. Not yet measured.
- Anime/Japan horror accounts (the hashtags #animehorror and #foundfootage returned nothing in my reads; try #japanhorror, #urbanlegend, #yokai, #kaiju, #shinjuku, #showa, #hououji).
- Follow-conversion: measure attributed follows per reel in creator Insights. Public views and current followers indicate relative scale only. Granite Waves has a visible episode catalog and app destination. Their conversions cannot be inferred from these counts.
- Non-IG research (YouTube, TikTok, Reddit r/nosleep, analog horror channels) not done.

## 7. What was NOT done / honest limits
- I cannot hear audio; the voice numbers are measurements, not listening.
- Tools used by Granite Waves are inferred, not confirmed.
- Reel 2 sound unmeasured.
- Story ideas were written by a different thread, not here.
- Nothing was liked, followed, commented or posted.

## 8. Next steps (suggested order)
1. Read the story files in `story/`.
2. Finish the open research gaps in section 6 (comments and retention first).
3. Lock the hook: one small wrongness in a normal place (the 5 O'CLOCK loudspeaker song), numbered logs/entries for serialization, original lore with rules.
4. Make one test shot in Blender Grease Pencil in the Granite Waves art style (only the style), with a real voice recorded for the line.
5. Keep updating this file.
