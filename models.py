from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    county = db.Column(db.String(100), nullable=False)
    town = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    modified_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    self_description = db.relationship('UserSelfDescription', backref='user', uselist=False)
    more_details = db.relationship('UserMoreDetails', backref='user', uselist=False)
    messages = db.relationship('Message', backref='user')
    match_requests = db.relationship('MatchRequest', backref='user')
    match_confirmations = db.relationship('MatchConfirmation', backref='user')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'county': self.county,
            'town': self.town
        }

class UserSelfDescription(db.Model):
    __tablename__ = "userselfdescription"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    modified_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message_direction = db.Column(db.Enum('Incoming', 'Outgoing'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class MatchRequest(db.Model):
    __tablename__ = "match_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    age_range = db.Column(db.String(20), nullable=False)
    county = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    
    # Relationships
    matches = db.relationship('Match', backref='request')
    confirmations = db.relationship('MatchConfirmation', backref='request')

class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey('match_requests.id', ondelete='CASCADE'), nullable=False)
    matched_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    displayed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class MatchConfirmation(db.Model):
    __tablename__ = "match_confirmations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match_requests.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    confirmation = db.Column(db.Enum('Yes', 'No'), nullable=False)
    confirmed_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class UserRequest(db.Model):
    __tablename__ = "user_requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    requested_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    status = db.Column(db.Enum('Pending', 'Sent'), nullable=False, default='Pending')
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], backref='requests_made')
    requested_user = db.relationship('User', foreign_keys=[requested_user_id], backref='requests_received')

class UserMoreDetails(db.Model):
    __tablename__ = "usermoredetails"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    level_of_education = db.Column(db.String(100))
    profession = db.Column(db.String(100))
    marital_status = db.Column(db.Enum('Single', 'Married', 'Divorced', 'Widowed'))
    religion = db.Column(db.String(100))
    ethnicity = db.Column(db.String(100))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    modified_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class MatchBatch(db.Model):
    __tablename__ = 'match_batches'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('match_requests.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_matches = db.Column(db.Integer)
    matches_shown = db.Column(db.Integer, default=0)
    match_data = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now())

    # Relationships
    request = db.relationship("MatchRequest", backref="match_batches")
    user = db.relationship("User", backref="match_batches")

