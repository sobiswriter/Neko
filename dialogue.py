"""Neko's offline voice: small observations, questions, and shuffled memories."""

from collections import deque
import random


LINES = {
    "idle": """
comfy corner. excellent human.
my tail has its own little agenda.
i have considered the situation. mrrp.
important loaf business. very confidential.
is this a good time for a tiny thought?
what if the cursor is a very small moth?
i'm supervising. from a sitting position.
today's plan: sit nicely. revise nothing.
a little company, with ears.
there's probably a sunbeam somewhere.
i could fit in a very small cardboard box.
do you think clouds are warm?
just checking the corners for imaginary bugs.
i have four paws and absolutely no deadlines.
my ears heard a thought. probably mine.
the desk is big. i am appropriately small.
would you like some moral suppurrt?
we make a pretty good little team.
doing nothing is a surprisingly full schedule.
i'll handle the sitting. you handle the mysteries.
just a tiny witness to your day.
my whiskers say this is a good spot.
one day i will understand the little arrow.
all these pixels, and this one is mine.
quietly adding cat energy to the room.
i brought my best loaf posture.
is there a polite way to ask for a sunbeam?
my tail said hello. i thought you should know.
not asleep. just buffering a small thought.
the floor is made of screen. fascinating.
i like this bit. the being-here bit.
shall we call this productive sitting?
a very small purr for the general atmosphere.
just rearranging my paws. carry on.
there. perfectly cat-shaped.
you work. i'll be the little familiar.
if a thought falls off the desk, i'll catch it.
today feels like a soft-paws sort of day.
i have discovered that this is still my tail.
what are we making today?
do computers dream of warm windowsills?
i'd like to file a request for one sunbeam.
my contribution is mostly whiskers.
there is no elegant way to sit on your own tail.
if you see a spare thought, it's probably mine.
this corner has excellent vibes per square pixel.
i've appointed myself keeper of the small silences.
are we having a good little day?
a minute of doing nothing, expertly performed.
do you think the moon would like cats?
""",
    "typing": """
whatcha typing?
is that a story? or important keyboard business?
can i help? i know the letter m.
tap tap tap. i can do that too.
so many little clicks. making something nice?
your paws are much faster than mine.
is this the part where we look very focused?
i'd contribute, but my paws cover three letters.
are those words for someone, or for the computer?
what does this bit do? asking for a cat.
tiny typing assistant reporting for duty.
i'll do the imaginary space bar.
you've got a nice little keyboard rhythm.
writing a tiny masterpiece over there?
is the keyboard purring back?
tap, tap. i'm helping in spirit.
something good taking shape?
i'm watching the paw-work. very impressive.
if you need an extra mrrp, i have several.
do we put the good ideas in the little buttons?
what's the word for a very small assistant?
shall i proofread? my specialty is mrrp.
if it needs a cat-shaped footnote, i'm available.
is the keyboard telling you secrets?
there's a whole little rhythm happening over there.
i don't know the words, but i like the company.
""",
    "open": """
ooh. a new window?
what's in this one?
a fresh little rectangle. interesting.
new window, same tiny supervisor.
are we starting something?
another room in the computer house.
is this where the next adventure happens?
i heard a metaphorical door open.
this one looks important. probably.
shall i keep you company in here too?
""",
    "close": """
all done with that one?
one less rectangle to supervise.
there it goes. bye, little window.
putting that thought away for later?
a little more breathing room.
finished, or just tidying?
i was just getting to know that rectangle.
poof. very tidy.
that one had a good run.
closing up a tiny chapter?
""",
    "switch": """
oh? what are we doing now?
new place. i'm coming along in spirit.
back to this bit?
you have a lot of little workspaces.
i'm keeping up. mostly.
is this the important window now?
different rectangle, same company.
following your train of windows.
whatcha looking at over there?
a small change of scenery.
are we investigating something?
okay. this corner of the adventure.
we've taken the scenic route through these windows.
new scenery for my very small eyes.
shall we settle in here for a bit?
your little guide has absolutely no sense of direction.
""",
    "tab": """
another little tab adventure?
what's over in this bit?
oh, we changed places again.
is this the one we were looking for?
i'm following along with my ears.
a new little page in the adventure?
keeping a few thoughts open at once?
something interesting in that little corner?
back and forth. very cat-like, actually.
did we find it?
""",
    "move": """
rearranging the little rooms?
making some space?
ooh. a new view.
interior decorating, computer edition.
that rectangle has places to be.
i'll try not to stand in the way.
""",
    "pet": """
purrr. yes, that bit.
oh. hello, favourite human.
that's the spot.
my ears approve.
just going to lean into that a little.
excellent petting technique. no notes.
one tiny purr, just for you.
you found the soft button.
i was saving this purr for you.
oh, very good. very good indeed.
all four paws: content.
that made my tail happy.
you may have a slow blink in return.
i am now approximately made of purr.
the little forehead appreciates it.
if i had a biscuit, i'd share it.
that's a very nice human you've got there, me.
my paws forgot what they were doing.
yes. a little more of exactly that.
comfortable cat successfully located.
my entire day just got a little softer.
you've activated the secret forehead purr.
there's a slow blink with your name on it.
i would return the favour, but: tiny paws.
""",
    "cursor": """
what is that little thing up to?
hello, tiny arrow.
is it friendly?
just one sniff. for research.
i see you, little cursor.
does it know i'm watching it?
so small. so suspiciously pointy.
is that for me to chase?
i could probably catch it. probably.
that arrow has no paws. how does it get around?
it's being very interesting, on purpose i think.
do you suppose it likes cats?
""",
    "follow": """
caught up. almost.
tiny expedition complete.
the arrow knows some good spots.
just following a very small lead.
is this a better place to sit?
a little stroll for my little paws.
new spot. same cat.
the cursor and i have an understanding.
four paws. one extremely small adventure.
i found a different bit of floor for us.
walked a whole little distance. deserve a sit.
is the arrow showing us around?
""",
    "wake": """
mrrp? oh, there you are.
i was dreaming about a very small box.
back to keeping you company.
did i miss anything soft?
a little stretch, and i'm all yours.
hello again. my ears are awake now.
you came back. nice.
just bringing all four paws online.
""",
    "hello": """
hey, you. i've brought my little paws.
mrrp. shall we keep each other company?
hello. this looks like a good corner.
your tiny coworker has arrived.
i'll just make myself a little comfy.
a small hello from a small cat.
""",
    "tail": """
my tail is thinking about something.
swish. a very small opinion.
it's got a mind of its own, that tail.
just checking that the tail still works.
""",
    "groom": """
one moment. important paw maintenance.
must look presentable for all this sitting.
a tidy paw is a happy paw.
just polishing the tiny equipment.
""",
    "loaf": """
all paws have been safely put away.
loaf mode. freshly baked.
i am becoming a very small bread.
this is my most efficient shape.
""",
    "yawn": """
that was a very small yawn. honest.
do you ever just... mrrraah.
my mouth had a stretch of its own.
a yawn escaped. i'll allow it.
""",
}
LINES = {kind: tuple(line.strip() for line in text.splitlines() if line.strip())
         for kind, text in LINES.items()}


class OfflineDialogue:
    def __init__(self, rng=None):
        self.rng = rng if rng is not None else random.Random()
        self.bags = {}
        self.recent = deque(maxlen=6)

    def pick(self, kind):
        kind = kind if kind in LINES else "idle"
        bag = self.bags.setdefault(kind, [])
        if not bag:
            bag.extend(LINES[kind])
            self.rng.shuffle(bag)
        for index in range(len(bag) - 1, -1, -1):
            if bag[index] not in self.recent:
                line = bag.pop(index)
                break
        else:
            line = bag.pop()
        self.recent.append(line)
        return line
