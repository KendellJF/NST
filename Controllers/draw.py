from datetime import datetime
import random
from sqlalchemy import func
from models import db, Entry

def getEligible():
    """Retrieve all entries that haven't been selected yet."""
    return Entry.query.filter(
        Entry.is_selected == False
    ).all()

def drawWinners():
    """Randomly select 4 winners from attended entries."""
    eligible_entries = getEligible()
    if not eligible_entries:
        return []

    num_winners = min(4, len(eligible_entries))
    winners = random.sample(eligible_entries, num_winners)

    for winner in winners:
        winner.is_selected = True
        # winner.selection_time = datetime.utcnow()
        db.session.add(winner)

    db.session.commit()
    return winners

def resetSelection():
    """Reset the selection status of all entries."""
    db.session.query(Entry).update({Entry.is_selected: False}, synchronize_session=False)
    db.session.commit()