"""Neko's offline voice: small observations, questions, and shuffled memories."""

from collections import deque
import random


LINES = {
    "idle": """
comfy corner. i'm glad you're here.
i like spending these little bits of the day with you.
you make a good window-watching buddy.
how's your little corner of the world today?
you can think out loud. i'm very good at listening quietly.
is there something you're looking forward to today?
you look like you could use a tiny coworker. convenient, that.
i saved you the imaginary sunny spot.
what would you do with an afternoon and absolutely no plans?
you and me. a pretty nice arrangement.
do you have a favourite kind of rainy day?
you don't have to entertain me. i like just being here with you.
if you're figuring something out, i'll sit with you while you do.
what's one small thing you liked about today?
you have a nice way of making this corner feel like home.
shall we have a little thinking quietly together?
you bring the ideas. i'll bring the extremely small paws.
if you need a little pause, you can borrow my loaf philosophy.
what's your favourite thing to listen to when you're making stuff?
i wonder what this day looks like from your side of the screen.
your company is my favourite part of the job.
my tail has its own little agenda. how about you?
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
you handle the deadlines. i have four paws to arrange.
my ears heard a thought. probably mine.
your desk is big. i am appropriately small.
would you like some moral suppurrt?
we make a pretty good little team.
doing nothing is a surprisingly full schedule.
i'll handle the sitting. you handle the mysteries.
just a tiny witness to your day.
my whiskers say this is a good spot to sit with you.
one day you'll have to explain that little arrow to me.
all these pixels, and this one is mine.
quietly adding cat energy to the room.
i brought you my best loaf posture.
is there a polite way to ask for a sunbeam?
my tail said hello. i thought you should know.
not asleep. just thinking about what you're making.
you get a whole room. my floor is made of screen. fascinating.
i like this bit. the being-here bit.
shall we call this productive sitting?
a very small purr for the general atmosphere.
just rearranging my paws. you carry on.
there. perfectly cat-shaped.
you work. i'll be the little familiar.
if a thought falls off the desk, i'll catch it.
i hope today is being gentle with you.
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
    "video": """
whatcha watching? may i sit with you?
are you picking something good? i've brought my sitting paws.
is it a movie night? i take up very little sofa.
you choose what to watch. i'll choose a comfy position.
what kind of story are you in the mood for?
may i be your tiny watch buddy?
if there's a cat in it, you'll tell me, right?
you handle the play button. i'll handle the loafing.
""",
    "music": """
whatcha listening to?
are you picking us a little soundtrack?
what's your favourite song at the moment?
you choose the music. my tail will keep imaginary time.
is it a soft-song day or a dance-in-your-chair day?
i'd share your headphones, but: ears.
may i be your tiny listening buddy?
is there a song that always makes you feel at home?
""",
    "coding": """
what are you building over there?
can your tiny assistant contribute one semicolon?
you write the clever bits. i'll supervise the brackets.
is this a little project or a big little project?
are you making something you wished existed?
if you need to explain a tricky bit, i can be your rubber cat.
you and your mysterious little curly brackets.
i hope your next run does exactly what you meant.
""",
    "drawing": """
whatcha making? something with colours?
you have a whole little canvas to play in.
can i nominate pink? for extremely professional reasons.
are you trying an idea or polishing one you already like?
you make the art. i'll hold a very still cat pose.
if you need a model with whiskers, i'm available.
what colour does today feel like to you?
may i sit here while you make something?
""",
    "writing": """
what are you writing? a thought you want to keep?
you bring the words. i'll bring the quiet company.
is this a story, a plan, or a collection of little thoughts?
you can start with the messy version. cats approve of drafts.
shall i save a tiny space for your next idea?
what's the bit you most want to get onto the page?
you and a blank page. lots of little possibilities.
i'll be here while you find the right words.
""",
    "chat": """
saying hello to someone? a little mrrp from me too.
you keeping someone company over there?
are you sending a little thought to a friend?
you do the talking. i'll wave with one tiny paw.
may your next conversation be a nice one.
i'd send a sticker, but i'm already one cat-shaped sticker.
you look like you're about to say something. i'm all ears.
is this the hello bit or the sending-memes bit?
""",
    "game": """
what are you thinking of playing?
you have the controls. i have moral suppurrt.
are you exploring somewhere new or visiting an old favourite?
you pick the adventure. i'll be your little familiar.
is this a cosy game kind of day?
if you need luck, i've brought four tiny paws of it.
may your next little adventure have excellent scenery.
i'll cheer very quietly from this corner.
""",
    "files": """
looking for something? i can offer a very serious sniff.
you've got a whole little cupboard of computer things.
are you finding an old favourite or putting something away?
you organise the folders. i'll organise these two front paws.
if the missing thing is cat-shaped, it's probably me.
having a little look through your stuff?
may you find exactly the little thing you wanted.
you and me on a tiny finding-things expedition.
""",
    "terminal": """
what are you asking the computer to do?
you speak fluent little blinking cursor, apparently.
shall i keep you company while it thinks?
you type a few words and things happen. very wizard-like.
i hope it answers you with something nice and boring.
are you running an experiment over there?
you look busy with some important little commands.
i'll keep my paws well away from the enter key.
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
swish, swoosh. i'm conducting the room.
my tail has a tiny dance to do.
my tail is thinking about something.
swish. a very small opinion.
it's got a mind of its own, that tail.
just checking that the tail still works.
""",
    "groom": """
oh! were you watching my beauty routine?
one ear polish. then i'm all yours.
one moment. important paw maintenance.
must look presentable for all this sitting.
a tidy paw is a happy paw.
just polishing the tiny equipment.
""",
    "loaf": """
fresh loaf! please admire gently.
paws tucked. maximum cozy achieved.
all paws have been safely put away.
loaf mode. freshly baked.
i am becoming a very small bread.
this is my most efficient shape.
""",
    "yawn": """
yaaawn... did my ears get taller?
big feelings. very small sleepy cat.
that was a very small yawn. honest.
do you ever just... mrrraah.
my mouth had a stretch of its own.
a yawn escaped. i'll allow it.
""",
    "tail_chase": """
Look at meeee!
Round.. around... around...
one more little circle! maybe two!
my tail keeps taking the scenic route.
very serious zoomie business happening here.
four paws, zero straight lines.
""",
    "tail_catch": """
gotcha, fluff!
wait. that wiggly thing belongs to me?
two paws. one very slippery plan.
you saw that little pounce, right?
tail inspection complete. suspiciously soft.
the tiniest victory for the tiniest hunter.
""",
    "stretch": """
biiiig stretch... tiny cat.
look how loooong my paws can go!
just unfolding my very important legs.
one little paw shake for good measure.
stretch first. supervise later.
""",
    "ears": """
did you hear that? my ears did!
left ear says mrrp. right ear agrees.
tiny antennas, reporting for duty.
something interesting? let me listen.
just tuning in to your little corner.
""",
    "sniff": """
sniff sniff... interesting!
one tiny nose investigation.
is that a new idea i smell?
my whiskers would like a closer look.
curiosity fits very nicely on my face.
""",
    "peek": """
just one eye open. for you.
i wasn't sleeping. i was secretly peeking.
oh! you're still here. good.
a little peek from the cozy department.
my ears woke up before the rest of me.
""",
    "look_left": """
something over there? let me look!
left-side inspection. very official.
my whiskers have a question about that corner.
just a curious little tilt this way.
""",
    "look_right": """
ooh. what's happening on this side?
right-side inspection. equally official.
this corner deserves a little head tilt too.
checking the other half of my tiny kingdom.
""",
}
LINES.update({
    "game_announce": """
ooh, that arrow… give me a moment!
i see a very catchable little arrow.
wait there. my paws are getting ready!
you brought the arrow over for me?
tiny hunter reporting for a tiny chase.
ears ready… paws nearly ready…
hold on, i need my pouncing face.
that wiggle looks suspiciously fun.
""",
    "game_go": """
Here I come! Tiny paws, big plans!
Here I come! That arrow is mine!
Here I come! Ready or meowt!
Here I come! Pounce time!
""",
    "game_pursuit": """
wait for my little legs!
zoom zoom, very serious kitten business!
i am speed. small speed.
just one teeny paw touch…
my ears are in chase mode!
you're wiggly. i like wiggly.
left paw, right paw, nearly there!
all four paws are doing their best!
the arrow has underestimated me.
little legs, don't fail me now!
my tail is helping. probably.
oh! a pounce-shaped opportunity!
""",
    "game_win": """
gotcha! did you see my paws?!
mine! i caught a whole arrow!
tiny hunter, enormous victory.
i did it! i actually did it!
that calls for a little happy dance.
please admire my excellent pouncing.
one arrow captured. many proud feelings.
can you tell i'm very pleased?
my paws would like a round of applause.
the arrow and i had a meeting. i won.
look! these are champion paws!
i shall be smug for one tiny moment.
""",
    "game_protest_high": """
no fair! my paws don't come with wings!
that's above my kitten ceiling!
come down a little, you sneaky arrow.
too high! i ordered a shorter sky.
""",
    "game_protest_low": """
hey! the arrow went under my paws!
too low! my nose is up here.
no fair hiding below the kitten floor.
come back up where my paws can reach!
""",
    "game_protest_side": """
no fair! that corner is outside my tiny kingdom.
hey, bring the arrow back over here!
my little legs have a travel limit!
that was a very sneaky sideways escape.
""",
    "game_protest_monitor": """
hey! you took my arrow to another screen!
no fair, my paws are on this monitor!
the arrow has left the kitten kingdom.
come back to my side of the desktop!
""",
    "game_loss": """
oh… my paws were so sure.
i almost had it. almost counts a little?
the arrow was extra slippery today.
i need a small sulk. and maybe a pet.
my tiny hunting feelings need a moment.
i'm folding up my paws for now.
that pounce looked better in my head.
hmph. a cuddle might fix this.
""",
    "game_comfort": """
oh… you came to check on me.
okay. one little cuddle helps.
my paws feel a bit braver now.
you can stay. especially your hand.
that's the exact pet i needed.
i forgive the arrow. mostly.
thank you for my little comfort break.
fine… i suppose i'm still your kitten.
""",
})
LINES = {kind: tuple(line.strip() for line in text.splitlines() if line.strip())
         for kind, text in LINES.items()}


class OfflineDialogue:
    def __init__(self, rng=None):
        self.rng = rng if rng is not None else random.Random()
        self.bags = {}
        self.last = {}
        self.recent = deque(maxlen=6)

    def pick(self, kind):
        kind = kind if kind in LINES else "idle"
        bag = self.bags.setdefault(kind, [])
        if not bag:
            bag.extend(LINES[kind])
            self.rng.shuffle(bag)
            if len(bag) > 1 and bag[-1] == self.last.get(kind):
                bag[0], bag[-1] = bag[-1], bag[0]
        for index in range(len(bag) - 1, -1, -1):
            if bag[index] not in self.recent and bag[index] != self.last.get(kind):
                line = bag.pop(index)
                break
        else:
            line = bag.pop()
        self.recent.append(line)
        self.last[kind] = line
        return line
