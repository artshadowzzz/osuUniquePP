osuUniquePP is an algorithm that is supposed to buff unique scores (per unique mod combination) and nerf non-unique/farm scores. 

The formula behind this looks like:

`scorePP * 1.15 - (0.006 * tpAmout)`

First of all, we check all the scores per unique mod combination and check if they pass threshold. To pass threshold, score should at least get 80% of pp player would get with that accuracy and full combo. For example:

[xi - FREEDOM DiVE [FOUR DIMENSIONS]](https://osu.ppy.sh/b/129891) + HDHR. First, we get all the scores with HDHR and then check if they pass threshold. In case of Freedom Dive we have only one score which passes the threshold: nathan on osu's one. The next one is Karthy's score and it doesn't pass threshold:

`575pp/800pp=0.72` 

And after calculating all scores with given mod combination, we count amount of scores passing threshold and use that in our formula to calculate new PP. For nathan on osu's score it will be:

`894.39 * (1.15 - (0.006 * 1)=1023.18`

So, the maximum buff is 15% at 1 score which passed threshold and the maximum nerf is 15% at 50 scores which passed threshold(i dont go past 50 tpAmout, coz it would be unreasonable to nerf **THAT MUCH**).
So, one score has the maximum buff amount of 15% since it has passed the threshold, while 50 scores have the maximum nerf amount of 15% which have all passed threshold (I don't go pst 50 tpAmout because it would be unreasonable to nerf them **THAT MUCH**)

Usage
======

To check user/map scores you need to install latest version of [Python](https://www.python.org/downloads/).
After that you need to download [latest version](https://github.com/artshadowzzz/osuUniquePP/releases) and set up your API key, which you can get at [this page](https://osu.ppy.sh/p/api) in config.json and after that run ppCalc.py with desired params.

**For the user check:**

```powershell
ppCalc.py -u user_id
```

For example:
```powershell
ppCalc.py -u 124493
```

**User check can take up to 3-5 minutes if maps from user's best scores are not in the database.**

**And for the map check:**

```powershell
ppCalc.py -b beatmapdiff_id mods
```

For example: 

```powershell
ppCalc.py -b 129891 HDHR
```

You can get beatmap difficulty id simply by going to the website and finding it in the link :`https://osu.ppy.sh/b/129891` and on the new one: `https://osu.ppy.sh/beatmapsets/39804#osu/129891`. `129891` is the beatmap difficulty id.

To check nomod scores just type "nomod" instead of mods.
