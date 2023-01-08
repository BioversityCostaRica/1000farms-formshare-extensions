from formshare.plugins.utilities import FormSharePublicView
from requests_oauthlib import OAuth2Session
from pyramid.httpexceptions import HTTPFound
from formshare.config.auth import get_user_data
from formshare.processes.db import update_last_login, register_user
from pyramid.security import remember
import datetime
import uuid
import secrets
from formshare.config.encdecdata import encode_data
from formshare.config.elasticfeeds import get_manager
from elasticfeeds.activity import Actor, Object, Activity
import logging
from formshare.processes.elasticsearch.user_index import get_user_index_manager

log = logging.getLogger("formshare")


class ClimMobLogin(FormSharePublicView):
    def process_view(self):
        session = self.request.session
        conf = self.request.registry.settings
        climmob = OAuth2Session(
            conf["climmobsso.client_id"], scope=conf["climmobsso.scope"]
        )
        authorization_url, state = climmob.authorization_url(
            conf["climmobsso.authorization_url"]
        )

        # State is used to prevent CSRF, keep this for later.
        session["climmob_oauth_state"] = state
        self.returnRawViewResult = True
        return HTTPFound(location=authorization_url)


class ClimMobLoginSuccess(FormSharePublicView):
    def process_view(self):
        session = self.request.session
        conf = self.request.registry.settings
        climmob = OAuth2Session(
            conf["climmobsso.client_id"],
            state=session["climmob_oauth_state"],
            redirect_uri=conf["climmobsso.redirect_url"],
        )
        self.returnRawViewResult = True
        climmob.fetch_token(
            conf["climmobsso.token_url"],
            client_secret=conf["climmobsso.client_secret"],
            authorization_response=self.request.url,
        )
        profile_info = climmob.get(conf["climmobsso.profile_url"]).json()
        user = get_user_data(self.request, profile_info["id"])
        login_data = {"login": profile_info["id"], "group": "mainApp"}
        if user is not None:
            update_last_login(self.request, user.login)
            headers = remember(self.request, str(login_data), policies=["main"])
            next_page = self.request.params.get("next") or self.request.route_url(
                "dashboard", userid=user.login
            )
            self.returnRawViewResult = True
            return HTTPFound(location=next_page, headers=headers)
        else:
            data = {
                "user_id": profile_info["id"],
                "user_name": profile_info["user_name"],
                "user_email": profile_info["email"],
                "user_cdate": datetime.datetime.now(),
                "user_apikey": str(uuid.uuid4()),
                "user_apisecret": encode_data(self.request, secrets.token_hex(16)),
            }
            added, error_message = register_user(self.request, data)
            if not added:
                self.append_to_errors(error_message)
            else:
                # Store the notifications
                feed_manager = get_manager(self.request)
                # The user follows himself
                try:
                    feed_manager.follow(data["user_id"], data["user_id"])
                except Exception as e:
                    log.warning(
                        "User {} was in FormShare at some point. Error: {}".format(
                            data["user_id"], str(e)
                        )
                    )
                # The user join FormShare
                actor = Actor(data["user_id"], "person")
                feed_object = Object("formshare", "platform")
                activity = Activity("join", actor, feed_object)
                feed_manager.add_activity_feed(activity)

                # Add the user to the user index
                user_index = get_user_index_manager(self.request)
                user_index_data = {
                    "user_id": data["user_id"],
                    "user_email": data["user_email"],
                    "user_name": data["user_name"],
                }
                user_index.add_user(data["user_id"], user_index_data)

                login_data = {
                    "login": data["user_id"],
                    "group": "mainApp",
                }
                headers = remember(
                    self.request,
                    str(login_data),
                    policies=["main"],
                )

                next_page = self.request.route_url("dashboard", userid=data["user_id"])
                self.returnRawViewResult = True
                return HTTPFound(next_page, headers=headers)

            self.returnRawViewResult = True
            return HTTPFound(self.request.route_url("climmob_login"))


class ClimMobLoginPage(FormSharePublicView):
    def process_view(self):
        return {}
