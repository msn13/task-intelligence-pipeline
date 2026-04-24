NOTES: list[str] = [
    # Note 1 — clear owner, soft deadline, mild urgency
    "Checked in with Mrs. Callahan in room 14 this afternoon. She's been having trouble sleeping and mentioned her anxiety has been worse since her daughter stopped visiting as regularly. Nurse Tompkins noted her appetite has also dropped over the last week or so. We talked about adjusting her evening routine and Dr. Patel said he'd follow up with a medication review sometime before the end of next week. Also need to reach out to the family liaison to get someone to contact the daughter — that's on me to do by Friday.",

    # Note 2 — multiple owners, vague timeframe, action buried mid-sentence
    "Team reviewed Mr. Okafor today. He's doing better overall after the fall last month but physical therapy says he's been skipping his afternoon sessions, apparently just doesn't want to go. His roommate situation might also be contributing — there's been some tension. Sandra from social work is going to talk to him one-on-one to figure out what's going on, she said she'd try to get that done this week if her schedule allows. We also flagged that his care plan hasn't been updated since February and someone needs to fix that before the next family meeting, which is the 30th.",

    # Note 3 — informal tone, no explicit owner on one item, deadline embedded naturally
    "Quick check-in on resident Flores. She seemed off today — kept repeating herself during our conversation and got frustrated when I pointed it out gently. Not sure if it's a bad day or something to watch. Dr. Nguyen wants a cognitive assessment scheduled ASAP, ideally within the next 5 days so we have something to show at the monthly review on the 28th. Her daughter also called yesterday asking about the status of the DNR paperwork and that's apparently still sitting somewhere unfinished — Alicia in admin was supposed to handle it two weeks ago.",

    # Note 4 — multiple action items, one with no owner assigned yet, urgency implied not stated
    "Resident Thompson had a rough week. Blood pressure's been inconsistent, 160 over 95 on Tuesday and then fine on Thursday. Dr. Brennan wants daily monitoring logged for the next 10 days and says if it spikes again we need to escalate before doing anything else. The night staff also mentioned he's been wandering after lights out, which is new. We don't have a great answer for that yet — someone needs to pull together a safety review but nobody's been assigned to it. Also his wheelchair needs a new cushion, the order was supposed to go in last week, Maria said she'd chase it down today.",

    # Note 5 — emotional/social context heavy, action items feel secondary, realistic team dynamic
    "Long meeting about Mrs. Delacroix. The family came in and they're not happy — feels like communication has broken down on our end honestly. She's been tearful most days, says she feels forgotten. We need to get a formal emotional wellness assessment done, James said he'd own that and wanted to have something back to the team by next Wednesday at the latest. The family also asked about moving her to a room closer to the common area and the facilities coordinator needs to check availability and get back to them within the week. One more thing — her prescription for the antidepressant runs out in about 8 days and nobody's put in the renewal yet.",
]


def get_note(index: int) -> str:
    """Returns notes from list for given index to be analyzed by Claude"""
    return NOTES[index % len(NOTES)]