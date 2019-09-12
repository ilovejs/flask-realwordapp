# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint
from flask_apispec import use_kwargs, marshal_with
from flask_jwt import current_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from .models import User
from .serializers import user_schema
from conduit.database import db
from conduit.exceptions import InvalidUsage
from conduit.extensions import cors
from conduit.profile.models import UserProfile
from conduit.utils import jwt_optional

# A blueprint is an object that allows defining application 
# functions without requiring an application object ahead of time.
blueprint = Blueprint('user', __name__)


@blueprint.route('/api/users', methods=('POST',))
@use_kwargs(user_schema)
@marshal_with(user_schema)
def register_user(username, password, email, **kwargs):
    try:
        # save user 
        # save user profile
        userprofile = UserProfile(
            User(username, email, password=password, **kwargs).save()
        ).save()
    except IntegrityError:
        # user_already_registered
        db.session.rollback()
        raise InvalidUsage.user_already_registered()
    return userprofile.user


@blueprint.route('/api/users/login', methods=('POST',))
@jwt_optional()
@use_kwargs(user_schema)
@marshal_with(user_schema)
def login_user(email, password, **kwargs):
    user = User.query.filter_by(email=email).first()
    if user is not None and user.check_password(password):
        return user
    else:
        raise InvalidUsage.user_not_found()


@blueprint.route('/api/user', methods=('GET',))
@jwt_required()
@marshal_with(user_schema)
def get_user():
    return current_identity


@blueprint.route('/api/user', methods=('PUT',))
@jwt_required()
@use_kwargs(user_schema)
@marshal_with(user_schema)
def update_user(**kwargs):
    # jwt facility
    # since we specify current user, api design won't have id
    user = current_identity
    # take in consideration the password
    password = kwargs.pop('password', None)
    if password:
        user.set_password(password)
    if 'updated_at' in kwargs:
        # replace time zone info
        kwargs['updated_at'] = user.created_at.replace(tzinfo=None)
    user.update(**kwargs)
    return user
