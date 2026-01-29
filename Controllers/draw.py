from datetime import datetime
import random
from sqlalchemy import func
from models import db, Entry

def getEligible():
    """Retrieve all eligible entries from the database."""
    return Entry.query.filter(
        Entry.c1 == True,
        Entry.c2 == True,
        Entry.c3 == True,
        Entry.c4 == True,
        Entry.is_selected == False
    ).all()

def drawWinners():
    """Randomly select winners from eligible entries."""
    eligible_entries = getEligible()
    if not eligible_entries:
        return []

    num_winners = min(num_winners, len(eligible_entries))
    winners = random.sample(eligible_entries, num_winners)

    for winner in winners:
        winner.is_selected = True
        # winner.selection_time = datetime.utcnow()
        db.session.add(winner)

    db.session.commit()
    return winners

def resetSelection():
    """Reset the selection status of all entries."""
    Entry.query.update({Entry.is_selected: False})
    db.session.commit()