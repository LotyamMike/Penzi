from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_
from models import User, UserMoreDetails, UserSelfDescription, MatchRequest, MatchConfirmation, Message, Match
from contextlib import contextmanager
from typing import List, Optional

app = Flask(__name__)

# Database connection
DATABASE_URL = "mysql+pymysql://root:Lotty%40488@localhost/Penzi_db"  # Updated to match your credentials
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Context manager for database sessions
@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def validate_request_data(data: dict, required_fields: List[str]) -> Optional[str]:
    """Validate request data against required fields"""
    if not data:
        return "No data provided"
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    return None

@app.route("/service-activation", methods=["POST"])
def service_activation():
    try:
        data = request.get_json()
        phone_number = data.get("from")  # Get sender's phone from SMS gateway
        message = data.get("message", "").strip().upper()
        
        if message == "PENZI":
            with get_session() as session:
                # Store phone number in match_requests for future matching
                existing_request = session.query(MatchRequest).filter_by(
                    phone_number=phone_number
                ).first()
                
                if existing_request:
                    return jsonify({
                        "message": "Welcome back to our dating service!\nTo search for a MPENZI, SMS match#age#town to 22141."
                    }), 200

            return jsonify({
                "message": "Welcome to our dating service with 6000 potential dating partners!\nTo register SMS start#name#age#gender#county#town to 22141.\nE.g., start#John Doe#26#Male#Nakuru#Naivasha"
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/register", methods=["POST"])
def register_user():
    try:
        data = request.get_json()
        phone_number = data.get("from")  # Get sender's phone from SMS gateway
        message = data.get("message", "")

        if not message.startswith("start#"):
            return jsonify({"message": "Invalid format. Use: start#name#age#gender#county#town"}), 400

        parts = message.split("#")
        if len(parts) != 6:  # start + 5 fields
            return jsonify({"message": "Invalid format. Use: start#name#age#gender#county#town"}), 400

        _, name, age, gender, county, town = parts

        with get_session() as session:
            # Create new user
            new_user = User(
                name=name,
                age=int(age),
                gender=gender,
                county=county,
                town=town
            )
            session.add(new_user)
            session.flush()  # Get the new user's ID

            # Create initial match record to store phone number
            initial_match = Match(
                request_id=1,  # You might want to handle this differently
                matched_user_id=new_user.id,
                phone_number=phone_number,
                displayed=False
            )
            session.add(initial_match)

            return jsonify({
                "message": f"Your profile has been created successfully {name}.\nSMS details#levelOfEducation#profession#maritalStatus#religion#ethnicity to 22141.\nE.g. details#diploma#driver#single#christian#mijikenda"
            }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/more-details", methods=["POST"])
def add_more_details():
    try:
        data = request.get_json()
        phone_number = data.get("from")  # Get sender's phone from SMS gateway
        message = data.get("message", "")

        if not message.startswith("details#"):
            return jsonify({"message": "Invalid format. Use: details#levelOfEducation#profession#maritalStatus#religion#ethnicity"}), 400

        # Find user_id from matches table using phone number
        with get_session() as session:
            match = session.query(Match).filter_by(phone_number=phone_number).first()
            if not match:
                return jsonify({"message": "Please register first"}), 404

            user_id = match.matched_user_id

            parts = message.split("#")
            if len(parts) != 6:  # details + 5 fields
                return jsonify({"message": "Invalid format. Use: details#levelOfEducation#profession#maritalStatus#religion#ethnicity"}), 400

            _, level_of_education, profession, marital_status, religion, ethnicity = parts

            more_details = UserMoreDetails(
                user_id=user_id,
                level_of_education=level_of_education,
                profession=profession,
                marital_status=marital_status,
                religion=religion,
                ethnicity=ethnicity
            )
            session.add(more_details)
            session.flush()

            return jsonify({
                "message": "This is the last stage of registration.\nSMS a brief description of yourself to 22141 starting with the word MYSELF.\nE.g., MYSELF chocolate, lovely, sexy etc."
            }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/self-description", methods=["POST"])
def add_self_description():
    try:
        data = request.get_json()
        phone_number = data.get("from")  # Get sender's phone from SMS gateway
        message = data.get("message", "")

        if not message.upper().startswith("MYSELF"):
            return jsonify({"message": "Invalid format. Start your description with MYSELF"}), 400

        # Find user_id from matches table using phone number
        with get_session() as session:
            match = session.query(Match).filter_by(phone_number=phone_number).first()
            if not match:
                return jsonify({"message": "Please register first"}), 404

            user_id = match.matched_user_id
            description = message[7:].strip()  # Remove "MYSELF " from the start

            self_desc = UserSelfDescription(
                user_id=user_id,
                description=description
            )
            session.add(self_desc)
            session.flush()

            return jsonify({
                "message": "You are now registered for dating.\nTo search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams.\nE.g., match#23-25#Kisumu"
            }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/match-request", methods=["POST"])
def request_match():
    try:
        data = request.get_json()
        phone_number = data.get("from")
        message = data.get("message", "")

        if not message.startswith("match#"):
            return jsonify({"message": "Invalid format. Use: match#age-range#town"}), 400

        parts = message.split("#")
        if len(parts) != 3:
            return jsonify({"message": "Invalid format. Use: match#age-range#town"}), 400

        _, age_range, town = parts

        with get_session() as session:
            # Find requesting user
            match_record = session.query(Match).filter_by(phone_number=phone_number).first()
            if not match_record:
                return jsonify({"message": "Please register first"}), 404

            requesting_user = session.query(User).get(match_record.matched_user_id)
            if not requesting_user:
                return jsonify({"message": "User not found"}), 404

            try:
                min_age, max_age = map(int, age_range.split('-'))
                if min_age < 18:
                    return jsonify({"message": "Minimum age must be 18 or above"}), 400
            except ValueError:
                return jsonify({"message": "Invalid age range format. Use: min-max (e.g., 23-25)"}), 400

            # Find total matches first
            opposite_gender = "Female" if requesting_user.gender == "Male" else "Male"
            total_matches = session.query(User).filter(
                User.gender == opposite_gender,
                User.age.between(min_age, max_age),
                User.county == town,
                User.id != requesting_user.id
            ).count()

            if total_matches == 0:
                return jsonify({
                    "message": f"No {opposite_gender.lower()} matches found in {town} between ages {min_age}-{max_age}"
                }), 200

            # Create match request
            match_request = MatchRequest(
                user_id=requesting_user.id,
                age_range=age_range,
                county=town,
                status="Pending"
            )
            session.add(match_request)
            session.flush()

            # Get first 3 matches with their details
            matches = session.query(User).filter(
                User.gender == opposite_gender,
                User.age.between(min_age, max_age),
                User.county == town,
                User.id != requesting_user.id
            ).limit(3).all()

            # Store matches and format response
            match_details = []
            for match in matches:
                new_match = Match(
                    request_id=match_request.id,
                    matched_user_id=match.id,
                    phone_number=phone_number,
                    displayed=False
                )
                session.add(new_match)
                match_details.append(f"{match.name} aged {match.age}, {match.county}")

            # Format response based on number of matches
            if total_matches <= 3:
                response = "\n".join(match_details)
            else:
                response = "\n".join(match_details)
                response += f"\nSend NEXT to 22141 to receive details of the remaining {total_matches - 3} {opposite_gender.lower()}s"

            return jsonify({"message": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/messages/<int:user_id>", methods=["GET"])
def get_messages(user_id):
    try:
        with get_session() as session:
            # Verify user exists
            user = session.query(User).get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            messages = session.query(Message).filter(
                or_(Message.sender_id == user_id, Message.receiver_id == user_id)
            ).order_by(Message.created_at.desc()).all()

            return jsonify({
                "messages": [msg.serialize() for msg in messages],
                "total_messages": len(messages)
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/next-matches", methods=["POST"])
def get_next_matches():
    try:
        data = request.get_json()
        phone_number = data.get("from")
        message = data.get("message", "").strip().upper()

        if message != "NEXT":
            return jsonify({"message": "Invalid command. Send NEXT to get more matches"}), 400

        with get_session() as session:
            # Find the user's latest match request
            match_record = session.query(Match).filter_by(phone_number=phone_number).first()
            if not match_record:
                return jsonify({"message": "No active match request found"}), 404

            # Get the latest match request
            latest_request = session.query(MatchRequest).filter_by(
                user_id=match_record.matched_user_id
            ).order_by(MatchRequest.id.desc()).first()

            if not latest_request:
                return jsonify({"message": "No active match request found"}), 404

            # Get next 3 undisplayed matches
            matches = session.query(User).filter(
                User.id.in_(
                    session.query(Match.matched_user_id)
                    .filter_by(request_id=latest_request.id, displayed=False)
                )
            ).limit(3).all()

            if not matches:
                return jsonify({"message": "No more matches available"}), 200

            # Mark these matches as displayed
            for match in matches:
                match_record = session.query(Match).filter_by(
                    request_id=latest_request.id,
                    matched_user_id=match.id
                ).first()
                if match_record:
                    match_record.displayed = True

            # Format response
            match_details = []
            for match in matches:
                match_phone = session.query(Match.phone_number).filter_by(
                    matched_user_id=match.id
                ).first()
                match_details.append(f"{match.name} aged {match.age}, {match_phone[0]}")

            response = "\n".join(match_details)

            # Count remaining undisplayed matches
            remaining = session.query(Match).filter_by(
                request_id=latest_request.id,
                displayed=False
            ).count()

            if remaining > 0:
                response += f"\nSend NEXT to 22141 to receive details of the remaining {remaining} matches"

            return jsonify({"message": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/profile-details", methods=["POST"])
def get_profile_details():
    try:
        data = request.get_json()
        requester_phone = data.get("from")  # Get sender's phone from SMS gateway
        message = data.get("message", "")  # This will be the match's phone number

        if not message.isdigit():
            return jsonify({
                "message": "Please send the phone number of the person you want to view"
            }), 400

        match_phone = message

        with get_session() as session:
            # Find requesting user from Match table
            requester_match = session.query(Match).filter(
                Match.phone_number.like(f"%{requester_phone[-9:]}")
            ).first()

            if not requester_match:
                return jsonify({"message": "Please register first"}), 404

            requester = session.query(User).get(requester_match.matched_user_id)

            # Find match from Match table
            match_record = session.query(Match).filter(
                Match.phone_number.like(f"%{match_phone[-9:]}")
            ).first()

            if not match_record:
                return jsonify({"message": "Match not found"}), 404

            match_user = session.query(User).get(match_record.matched_user_id)
            match_details = session.query(UserMoreDetails).filter_by(user_id=match_user.id).first()

            if not match_details:
                return jsonify({"message": "Match details not found"}), 404

            # Create match request
            match_request = MatchRequest(
                user_id=requester.id,
                age_range=f"{match_user.age-2}-{match_user.age+2}",
                county=match_user.county,
                status="pending"
            )
            session.add(match_request)
            session.commit()

            # Format messages for both parties
            requester_message = (
                f"{match_user.name} aged {match_user.age}, {match_user.county} County, "
                f"{match_user.town} town, {match_details.level_of_education}, "
                f"{match_details.profession}, {match_details.marital_status}, "
                f"{match_details.religion}, {match_details.ethnicity}.\n"
                f"Send DESCRIBE {match_record.phone_number} to get more details about {match_user.name}"
            )

            match_notification = (
                f"Hi {match_user.name}, "
                f"a {requester.gender.lower()} called {requester.name} is interested in you "
                f"and requested your details.\n"
                f"They are aged {requester.age} based in {requester.county}.\n"
                f"Do you want to know more about them? Send YES to 22141"
            )

            return jsonify({
                "message": requester_message,
                "notification": match_notification
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/describe", methods=["POST"])
def get_description():
    try:
        data = request.get_json()
        requester_phone = data.get("from")
        message = data.get("message", "")

        # Check if message starts with DESCRIBE
        if not message.startswith("DESCRIBE"):
            return jsonify({"message": "Invalid format. Use: DESCRIBE phone_number"}), 400
        # Extract phone number from message
        parts = message.split()
        if len(parts) != 2:
            return jsonify({"message": "Invalid format. Use: DESCRIBE phone_number"}), 400

        target_phone = parts[1]

        with get_session() as session:
            # Find requesting user - handle different phone number formats
            requester_match = session.query(Match).filter(
                Match.phone_number.like(f"%{requester_phone[-9:]}")  # Match last 9 digits
            ).first()

            if not requester_match:
                return jsonify({"message": "Please register first"}), 404

            # Find target user - handle different phone number formats
            target_match = session.query(Match).filter(
                Match.phone_number.like(f"%{target_phone[-9:]}")  # Match last 9 digits
            ).first()

            if not target_match:
                return jsonify({"message": "User not found"}), 404

            target_user = session.query(User).get(target_match.matched_user_id)
            
            # Get description from UserSelfDescription table
            user_description = session.query(UserSelfDescription).filter_by(user_id=target_user.id).first()
            if not user_description:
                return jsonify({"message": "Description not found"}), 404

            # Set pronoun based on gender
            pronoun = "himself" if target_user.gender == "Male" else "herself"

            # Format response with correct gender pronoun and description
            response = (
                f"{target_user.name} describes {pronoun} as {user_description.description}"
            )

            return jsonify({"message": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/confirm-interest", methods=["POST"])
def confirm_interest():
    try:
        data = request.get_json()
        responder_phone = data.get("from")
        message = data.get("message", "")

        if message.upper() != "YES":
            return jsonify({"message": "Invalid format. Please reply with YES"}), 400

        with get_session() as session:
            # Find the user who was requested (the responder)
            responder_match = session.query(Match).filter(
                Match.phone_number.like(f"%{responder_phone[-9:]}")  # Match last 9 digits
            ).first()

            if not responder_match:
                return jsonify({"message": "User not found in matches"}), 404

            responder = session.query(User).get(responder_match.matched_user_id)

            # Find who requested their details (the requester)
            latest_request = session.query(MatchRequest).filter(
                MatchRequest.county == responder.county,
                MatchRequest.status == "pending"
            ).order_by(MatchRequest.id.desc()).first()

            if not latest_request:
                return jsonify({"message": "No pending requests found"}), 404

            # Get the requester's details
            requester = session.query(User).get(latest_request.user_id)
            if not requester:
                return jsonify({"message": "Requester not found"}), 404

            requester_match = session.query(Match).filter_by(matched_user_id=requester.id).first()
            if not requester_match:
                return jsonify({"message": "Requester match not found"}), 404

            requester_details = session.query(UserMoreDetails).filter_by(user_id=requester.id).first()
            if not requester_details:
                return jsonify({"message": "Requester details not found"}), 404

            # Format response exactly as specified
            response = (
                f"{requester.name} aged {requester.age}, {requester.county} County, "
                f"{requester.town} town, {requester_details.level_of_education}, "
                f"{requester_details.profession}, {requester_details.marital_status}, "
                f"{requester_details.religion}, {requester_details.ethnicity}.\n"
                f"Send DESCRIBE {requester_match.phone_number} to get more details about {requester.name}"
            )

            # Update match request status to '1' instead of 'confirmed'
            latest_request.status = "1"  # Using '1' as it's likely the valid status value
            session.commit()

            return jsonify({"message": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
