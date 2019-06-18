osuUniquePP is an algorithm supposed to buff unique scores(per unique mod combination) and nerf the non-unique/farm scores. 

The formula behind this looks like:

`scorePP * 1.15 - (0.006 * tpAmout)`

First of all, we check all the scores per unique mod combination and check if they pass threshold. To pass threshold score should get alteast 80% of pp player would get with that accuracy full combo. For example:

We have [xi - FREEDOM DiVE [FOUR DIMENSIONS]](https://osu.ppy.sh/b/129891) + HDHR. First we get all the scores with HDHR and then check every of them if they pass threshold. In case of Freedom Dive we have only one score which pass threshold and its nathan on osu's one. The next one score is Karthy's score and it doesnt pass threshold:

`575pp/800pp=0.72` 

And after calculating all scores with given mod combination we count amout of scores passed threshold and use that in our formula to calculate new PP. For nathan on osu's score it will be:

`894.39 * (1.15 - (0.006 * 1)=1023.18`

So the maximum buff is 15% at 1 score which passed threshold and the maximum nerf is 15% at 50 scores which passed threshold(i dont go past 50 tpAmout, coz it would be unreasonable to nerf **THAT MUCH**).

Usage
======

To check user/map scores first of all you need to install latest version of [Python](https://www.python.org/downloads/).
After that you need to download [latest version](https://github.com/artshadowzzz/osuUniquePP/releases) and set up your API key in which you can get at [that page](https://osu.ppy.sh/p/api) in config.json and after that run ppCalc.py with desired params.

**For user check:**

```powershell
ppCalc.py -u user_id
```

For example:
```powershell
ppCalc.py -u 124493
```

**User check can get up to 3-5 minutes if maps from user's best scores arent in base.**

**And for map check:**

```powershell
ppCalc.py -b beatmapdiff_id mods
```

For example: 

```powershell
ppCalc.py -b 129891 HDHR
```

You can get beatmap difficulty id simply by going to the site and find that in the link :`https://osu.ppy.sh/b/129891` and on the new one: `https://osu.ppy.sh/beatmapsets/39804#osu/129891`. `129891` is the beatmap difficulty id.

To check nomod scores just write nomod instead of mods.
