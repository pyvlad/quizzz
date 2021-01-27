import pytest

from quizzz.db import get_db_session
from quizzz.groups.models import Group, Member

from .data import GROUPS, MEMBERSHIPS, USERS


def test_user_groups(client, auth):
    """
    Test the <index> view:
    a. it should not be available to anonymous users;
    b. it should list only groups and group links that belong to current user;
    c. there should be a form to join new groups;
    """
    response = client.get('/groups/')
    assert response.status_code == 401

    auth.login_as("bob")

    response = client.get('/groups/')
    assert response.status_code == 200

    user_group_ids = [m["group_id"] for m in MEMBERSHIPS if m["user_id"] == USERS["bob"]["id"]]
    user_group_names = [g["name"] for g in GROUPS.values() if g["id"] in user_group_ids]
    for group_name in user_group_names:
        assert group_name.encode() in response.data
    for group_id in user_group_ids:
        assert (f"/groups/{group_id}/").encode() in response.data

    other_group_names = [g["name"] for g in GROUPS.values() if g["id"] not in user_group_ids]
    for group_name in other_group_names:
        assert group_name.encode() not in response.data

    assert b"/groups/join" in response.data



def test_join_group(app, client, auth):
    """
    Test the <join> view:
    a. it should not be available to anonymous users;
    b. 400 is returned if incorrect form data is submitted;
    c. friendly messages are shown on joining a joined group, submitting 
       invalid invitation code, or joining a group that reached its member limit;
    d. joining another group works;
    """
    response = client.post('/groups/join')
    assert response.status_code == 401

    auth.login_as("bob")
    response = client.post('/groups/join', data={})
    assert response.status_code == 302
    assert b'Invalid form submitted.' in client.get(response.headers["LOCATION"]).data

    initial_user_groups = [m["group_id"] for m in MEMBERSHIPS if m["user_id"] == USERS["bob"]["id"]]

    response = client.post('/groups/join',
        data={"invitation_code": GROUPS["group2"]["invitation_code"]}, follow_redirects=True)
    assert b"Joined!" in response.data
    with app.app_context():
        # new membership should be in database now
        db = get_db_session()
        new_user_groups = db.query(Member.group_id).filter(Member.user_id == USERS["bob"]["id"]).all()
        assert len(new_user_groups) == len(initial_user_groups) + 1

    response = client.post('/groups/join',
        data={"invitation_code": GROUPS["group1"]["invitation_code"]}, follow_redirects=True)
    assert b"You are already a member of this group!" in response.data

    response = client.post('/groups/join',
        data={"invitation_code": "some wrong code"}, follow_redirects=True)
    assert b"Invalid invitation code!" in response.data

    # test limit on group members
    with app.app_context():
        db = get_db_session()
        member_count = db.query(Member).filter(Member.group_id == GROUPS["group2"]["id"]).count()
    assert member_count == GROUPS["group2"]["max_members"]    # make sure limit is already reached
    auth.login_as("lucy")
    response = client.post('/groups/join', 
        data={"invitation_code": GROUPS["group2"]["invitation_code"]}, follow_redirects=True)

    # explanation is shown to the user:
    assert b"Too many members" in response.data
    # member count hasn't changed:
    with app.app_context():
        db = get_db_session()
        member_count = db.query(Member).filter(Member.group_id == GROUPS["group2"]["id"]).count()
    assert member_count == GROUPS["group2"]["max_members"]    



def test_group_page(client, auth):
    """
    Test the <show_group_page> view:
    a. Unavailable for anonymous users;
    b. Unavailable for non-members;
    c. Available for members;
    """
    response = client.get('/groups/1/')
    assert response.status_code == 401

    auth.login_as("bob")
    response = client.get('/groups/2/')
    assert response.status_code == 403

    response = client.get("/groups/1/")
    assert response.status_code == 200
