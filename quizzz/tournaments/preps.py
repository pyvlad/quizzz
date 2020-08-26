import datetime

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
    <tournament.rounds>, <round.plays>, <play.user> related objects,
    calculate and return a jsonifiable list for the "standings" table
    of the "show_tournament_page" view.
    """
    total_points = {}
    total_plays = {}
    user_names = {}

    for round in tournament_obj.rounds:
        round_standings = prep_round_standings(round.plays)
        for play in round_standings:
            user_id = play["user_id"]
            total_plays[user_id] = total_plays.get(user_id, 0) + 1
            total_points[user_id] = total_points.get(user_id, 0) + play["points"]
            user_names[user_id] = user_names.get(user_id, play["user"])

    standings = [
        {
            "user_id": x[0],
            "user": user_names[x[0]],
            "points": x[1],
            "rounds": total_plays[x[0]]
        } for x in sorted(total_points.items(), key=lambda x:x[1], reverse=True)
    ]

    return standings
