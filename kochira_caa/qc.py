"""
Quality control for fansubbers living in the future.
"""
from operator import itemgetter

from kochira.service import Service, requires_context, requires_permission

# improvements: add who to QCItem
# search for items around a time

class QCItem:
    def __init__(self, time, text, done=False):
        self.time = time
        self.text = text
        self.done = done

    def __lt__(self, other):
        return self.time < other.time

service = Service(__name__, __doc__)

@service.setup
def setup_contexts(ctx):
    ctx.storage.items = []

@service.command(r"^(?P<time>[0-9]{2}:[0-9]{2}) (?P<text>.*)")
@requires_context("qc")
def add_qcitem(ctx, time, text):
    """Adds a QC item to the list."""
    ctx.storage.items.append(QCItem(time, text, False))
    ctx.message("\x02#{num}:\x02 [{time}] {text}".format(
        num=len(ctx.storage.items),
        time=time,
        text=text
    ))

@service.command(r"(?:cancel|forget(?: about)?|delete|remove) #(?P<num>[0-9]+).*$")
@requires_context("qc")
def del_qcitem(ctx, num):
    """Removes a QC item (without marking it as complete)."""
    num = int(num)
    if num > len(ctx.storage.items) or num <= 0:
        ctx.respond("We don't have a \x02#{num}\x02 yet!".format(num=num))
        return

    del ctx.storage.items[num - 1]
    ctx.respond("\x02#{num}\x02 deleted!".format(num=num))

@service.command(r"(?:fixed|done(?: with)?|finished|reject|wontfix) #(?P<num>[0-9]+).*$")
def done_qcitem(ctx, num):
    """Marks an item as done."""
    num = int(num)
    if num > len(ctx.storage.items) or num <= 0:
        return

    ctx.storage.items[num - 1].done = True
    ctx.message("\x02#{num}:\x02 done".format(num=num))

@service.command(r"(?:what's left|^!?todo|^!list)")
@requires_context("qc")
def list_qcitems(ctx):
    """Displays a list of things to do."""
    todo = [(idx, item) for idx, item in enumerate(ctx.storage.items) if not item.done]
    for num, i in sorted(todo, key=itemgetter(1)):
        ctx.message("\x02#{num}:\x02 [{i.time}] {i.text}".format(
            num=num+1,
            i=i))

    ctx.message("===== END QC LIST ({count} ITEMS, {total} TOTAL) =====".format(
        count=len(todo),
        total=len(ctx.storage.items)
    ))

@service.command(r"!qc$")
@requires_permission("qcmaster")
def enter_qcmode(ctx):
    ctx.storage.items = []
    ctx.add_context("qc")
    ctx.message("===== BEGIN QC MODE =====")

@service.command(r"!stopqc$")
@requires_permission("qcmaster")
def exit_qcmode(ctx):
    ctx.remove_context("qc")
    ctx.message("===== END QC MODE ({count} ITEMS, {done} DONE) =====".format(
        count=len(ctx.storage.items),
        done=len([x for x in ctx.storage.items if x.done])
    ))

