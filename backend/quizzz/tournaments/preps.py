import datetime
from collections import defaultdict

from flask import url_for
from quizzz.momentjs import momentjs



def prep_tournament(tournament):
    """
    Given <tournament> ORM object return its jsonifiable representation.
    """
    return {
        "id": tournament.id,
        "name": tournament.name,
        "is_active": tournament.is_active,
        "time_created": tournament.time_created,
        "view_url": url_for('tournaments.show_tournament_page', tournament_id=tournament.id),
        "edit_url": url_for('tournaments.edit_tournament', tournament_id=tournament.id),
    }



def prep_round(round, user_id, now=None):
    """
    Given <round> ORM object with pre-loaded
    <round.tournament>, <round.quiz>, <round.plays>, and <round.quiz.author>
    related objects, return a jsonifiable representation of the round.
    """
    users_played = set(play.user.id for play in round.plays)

    return {
        "id": round.id,
        "start_time":  momentjs(round.start_time)._timestamp_as_iso_8601(),
        "finish_time": momentjs(round.finish_time)._timestamp_as_iso_8601(),
        "status": round.get_status(now=now),
        "is_taken": user_id in users_played,
        "is_author": round.is_authored_by(user_id),
        "author_score": round.get_author_score(),
        "edit_url": url_for('tournaments.edit_round', tournament_id=round.tournament.id, round_id=round.id), # TODO get rid of round.tournament?
        "view_url": url_for('tournaments.show_round_page', round_id=round.id),
        "quiz": {
            "id": round.quiz.id,
            "topic": round.quiz.topic,
            "author": round.quiz.author.name
        },
    }



def prep_round_list(tournament, user_id, now=None):
    """
    Given <tournament> ORM object with pre-loaded
    <tournament.rounds>, <round.quiz> and <round.plays> related objects,
    return a jsonifiable list of rounds to be used in the "show_tournament_page" view.
    """
    if now is None:
        now = datetime.datetime.utcnow()

    return [prep_round(round, user_id, now=now) for round in tournament.rounds]



def prep_round_standings(round_plays):
    """
    Given <round> ORM object with pre-loaded <round.plays> and <play.user> related objects,
    calculate and return a jsonifiable list for the "standings" table.
    """
    plays = [
        {
            "id": play.id,
            "user": play.user.name,
            "user_id": play.user.id,
            "result": play.result,
            "time": play.get_server_time(),
            "score": play.get_score()
        }
        for play in round_plays
    ]
    standings = sorted(plays, key=lambda x: x["score"], reverse=True)
    num_participants = len(standings)
    for i, play in enumerate(standings):
        play["points"] = num_participants - i

    return standings



def prep_tournament_standings(tournament_obj):
    """
    Given <tournament> ORM object with pre-loaded
    <tournament.rounds>, <round.quiz>, <quiz.author>, <round.plays>, <play.user> related objects,
    calculate and return a jsonifiable list for the "standings" table
    of the "show_tournament_page" view.
    """
    points_total = defaultdict(int)
    points_played = defaultdict(int)
    points_authored = defaultdict(int)
    rounds_total = defaultdict(int)
    rounds_played = defaultdict(int)
    rounds_authored = defaultdict(int)
    user_names = {}

    for round in tournament_obj.rounds:
        round_standings = prep_round_standings(round.plays)
        for play in round_standings:
            user_id = play["user_id"]
            rounds_total[user_id] += 1
            rounds_played[user_id] += 1
            points_total[user_id] += play["points"]
            points_played[user_id] += play["points"]
            user_names[user_id] = user_names.get(user_id, play["user"])
        author_id = round.quiz.author_id
        if author_id:
            rounds_total[author_id] += 1
            rounds_authored[author_id] += 1
            points_total[author_id] += round.get_author_score()
            points_authored[author_id] += round.get_author_score()
            user_names[author_id] = user_names.get(author_id, round.quiz.author.name)

    standings = [
        {
            "user_id": x[0],
            "user": user_names[x[0]],
            "points": x[1],
            "rounds": rounds_total[x[0]],
            "points_played": points_played.get(x[0], 0),
            "points_authored": points_authored.get(x[0], 0),
            "rounds_played": rounds_played.get(x[0], 0),
            "rounds_authored": rounds_authored.get(x[0], 0)
        } for x in sorted(points_total.items(), key=lambda x:x[1], reverse=True)
    ]

    return standings
