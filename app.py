from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from sqlalchemy import func, distinct, cast, Date
import json
from datetime import datetime
from models import User, Match, UserMoreDetails, UserSelfDescription, Message, MatchRequest, MatchBatch
from database import get_session

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Add headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# Test route to verify server is running
@app.route("/")
def home():
    return "Penzi SMS Server is running"

@app.route("/test-db", methods=['GET'])
def test_db():
    try:
        with get_session() as session:
            users_count = session.query(User).count()
            return jsonify({
                "status": "success",
                "message": "Database connected successfully",
                "users_count": users_count
            })
    except Exception as e:
        print(f"Database Error: {str(e)}")  # Print error to console
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500

@app.route("/receive-sms", methods=["POST"])
def receive_sms():
        if message != "PENZI":
            return jsonify({
                "message": "To register please send PENZI to 22141"
            }), 400

        with get_session() as session:
            # Check if user exists in Match table first
            existing_match = session.query(Match).filter_by(phone_number=phone_number).first()
                
            if existing_match:
                return jsonify({
                    "message": "Welcome back to our dating service!\nTo search for a MPENZI, SMS match#age#town to 22141."
                }), 200

            # New user
            return jsonify({
                "message": "Welcome to our dating service with 6000 potential dating partners!\nTo register SMS start#name#age#gender#county#town to 22141.\nE.g., start#John Doe#26#Male#Nakuru#Naivasha"
            }), 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
        return jsonify({"error": str(e)}), 500

    try:
        data = request.get_json()
        phone_number = data.get("from")  # Get sender's phone from SMS gateway
        message = data.get("message", "")

        if not message.startswith("start#"):
            return jsonify({"message": "Invalid format. Use: start#name#age#gender#county#town"}), 400

            new_user = User(
                name=name,
                age=int(age),
                gender=gender,
                county=county,
                town=town
            )
            session.add(new_user)
            session.flush()  # Get the new user's ID

            # Create initial match request with 'Pending' status
            match_request = MatchRequest(
                user_id=new_user.id,
                age_range="18-99",  # Default range
                county=county,
                status="Pending"  # Changed from 'Initial' to 'Pending'
            )
            session.add(match_request)
            session.flush()




                store_message(session, new_user.id, "outgoing", response)
            session.commit()
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
                    user_id=user.id,
                    level_of_education=level_of_education,
                    profession=profession,
                    marital_status=marital_status,
                    religion=religion,
                    ethnicity=ethnicity
                )
                session.add(more_details)

                response = (
                    "This is the last stage of registration.\n"
                    "SMS a brief description of yourself to 22141 starting with the word MYSELF.\n"
                    "E.g., MYSELF chocolate, lovely, sexy etc."
                )

            # Response message
            response_text = "This is the last stage of registration.\nSMS a brief description of yourself to 22141 starting with the word MYSELF.\nE.g., MYSELF chocolate, lovely, sexy etc."

            # Store the outgoing response message
            outgoing_message = Message(
                user_id=user_id,
                message_direction="outgoing",
                message_text=response_text
            )
            session.add(outgoing_message)

            session.commit()
                return jsonify({"message": response}), 200

            return jsonify({
                "message": response_text
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
                
                if not description:
                    error_msg = "Please provide a description after MYSELF"
                    store_message(session, user.id, "outgoing", error_msg)
                    return jsonify({"message": error_msg}), 400

            self_desc = UserSelfDescription(
                    user_id=user.id,
                    description=description
                )
                session.add(self_desc)

            # Store the incoming self-description message
            incoming_message = Message(
                user_id=user_id,
                message_direction="incoming",
                message_text=message
            )
            session.add(incoming_message)

            # Response message
            response_text = "You are now registered for dating.\nTo search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams.\nE.g., match#23-25#Kisumu"

            # Store the outgoing response message
            outgoing_message = Message(
                user_id=user_id,
                message_direction="outgoing",
                message_text=response_text
            )
            session.add(outgoing_message)

                store_message(session, user.id, "outgoing", response)
            session.commit()

            elif message_upper.startswith("MATCH#"):
        parts = message.split("#")
        if len(parts) != 3:
            return jsonify({
                "message": "Invalid format. Use: match#age-range#town\nE.g., match#23-25#Nairobi"
            }), 400

        _, age_range, town = parts

        with get_session() as session:
            # Debug: Print all users
            all_users = session.query(User).all()
            print("\nAll Users in Database:")
            for user in all_users:
                print(f"- {user.name}, Age: {user.age}, Gender: {user.gender}, County: {user.county}")

            # Find requesting user
            requester_match = session.query(Match).filter(
                or_(
                    Match.phone_number == phone_number,
                    Match.phone_number.like(f"%{phone_number[-9:]}")
                )
            ).first()

            if not requester_match:
                return jsonify({"message": "Please register first"}), 404

            requesting_user = session.query(User).get(requester_match.matched_user_id)
            if not requesting_user:
                return jsonify({"message": "User not found"}), 404

            print(f"\nRequesting User: {requesting_user.name}, Gender: {requesting_user.gender}")

            try:
                min_age, max_age = map(int, age_range.split('-'))
                if min_age < 18:
                    return jsonify({"message": "Minimum age must be 18 or above"}), 400
            except ValueError:
                return jsonify({
                    "message": "Invalid age range format. Use: min-max (e.g., 23-25)"
                }), 400

            # Simple direct query to find matches
            opposite_gender = "Female" if requesting_user.gender == "Male" else "Male"
            
            print(f"\nSearching for:")
            print(f"- Gender: {opposite_gender}")
            print(f"- Age Range: {min_age}-{max_age}")
            print(f"- County: {town}")

            # First get matching users
            matching_users = session.query(User).filter(
                User.gender == opposite_gender,
                User.age.between(min_age, max_age),
                func.lower(User.county) == func.lower(town)
            ).all()

            print(f"\nFound {len(matching_users)} users matching criteria:")
            for user in matching_users:
                print(f"- {user.name}, Age: {user.age}, Gender: {user.gender}, County: {user.county}")

            # Create a new match request record with correct column names
            match_request = MatchRequest(
                user_id=requesting_user.id,
                age_range=age_range,
                county=town,  # Changed to match the actual column name
                status="Pending"
            )
            session.add(match_request)
            session.flush()  # Get the ID without committing

            # Get matching users and their phone numbers
            matches = []
            match_data = []  # For storing in match_batches
            
            for user in matching_users:
                latest_match = session.query(Match).filter(
                    Match.matched_user_id == user.id,
                    Match.phone_number != None
                ).order_by(Match.id.desc()).first()
                
                if latest_match and latest_match.phone_number:
                    matches.append((user, latest_match))
                    # Store match data for batch processing
                    match_data.append({
                        "name": user.name,
                        "age": user.age,
                        "phone": latest_match.phone_number,
                        "user_id": user.id
                    })

            total_matches = len(matches)

            if total_matches == 0:
                return jsonify({
                    "message": f"No {opposite_gender.lower()} matches found in {town} between ages {min_age}-{max_age}"
                }), 200

            # Create match batch record
            match_batch = MatchBatch(
                request_id=match_request.id,
                user_id=requesting_user.id,
                total_matches=total_matches,
                matches_shown=min(3, total_matches),  # Initial matches shown
                match_data=json.dumps(match_data)
            )
            session.add(match_batch)

            # Format initial message
            if opposite_gender == "Female":
                gender_term = "lady" if total_matches == 1 else "ladies"
            else:
                gender_term = "man" if total_matches == 1 else "men"

            initial_message = f"We have {total_matches} {gender_term} who match your choice!"
            if total_matches > 3:
                initial_message += "\nWe will send you details of 3 of them shortly."
            initial_message += f"\nTo get more details about a {gender_term}, SMS their number e.g., 0722010203 to 22141"

            # Format match details (first 3)
            match_details = []
                for match_user, match_record in display_matches:
                    match_details.append(
                        f"{match_user.name} aged {match_user.age}, {match_record.phone_number}."
                    )
            session.add(incoming_message)

            # Combine messages
            response = initial_message + "\n\n" + "\n".join(match_details)

            # Add NEXT instruction if more than 3 matches
            if total_matches > 3:
                remaining = total_matches - 3
                response += f"\n\nSend NEXT to 22141 to receive details of the remaining {remaining} {gender_term}"

                store_message(session, user.id, "outgoing", matches_response)
                session.commit()

    except Exception as e:
        print(f"Error: {str(e)}")
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
            # Get the requesting user's match record
            requesting_match = session.query(Match).filter_by(
                phone_number=phone_number
            ).first()

            if not requesting_match:
                return jsonify({"message": "No active match request found"}), 404

            # Get the latest match batch for this user
            match_batch = session.query(MatchBatch).filter_by(
                user_id=requesting_match.matched_user_id
            ).order_by(MatchBatch.id.desc()).first()

            if not match_batch:
                return jsonify({"message": "No active match request found"}), 404

            match_data = json.loads(match_batch.match_data)

            # Get remaining matches
            remaining_matches = match_data[match_batch.matches_shown:]

            if not remaining_matches:
                response_text = "No more matches available"
                outgoing_message = Message(
                    user_id=requesting_match.matched_user_id,
                    message_direction="outgoing",
                    message_text=response_text
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": response_text}), 200

            # Take next 2 matches
            current_batch = remaining_matches[:2]
            
            # Format match details
            match_details = []
            for match in current_batch:
                match_details.append(f"{match['name']} aged {match['age']}, {match['phone']}")

            response = "\n".join(match_details)

            # Update matches shown count
            match_batch.matches_shown += len(current_batch)

            # Calculate remaining matches
            remaining = len(remaining_matches) - len(current_batch)

            if remaining > 0:
                # Get gender info for proper terminology
                requesting_user = session.query(User).get(requesting_match.matched_user_id)
                opposite_gender = "Female" if requesting_user.gender == "Male" else "Male"
                remaining_term = "lady" if opposite_gender == "Female" and remaining == 1 else \
                               "ladies" if opposite_gender == "Female" else \
                               "man" if remaining == 1 else "men"
                response += f"\nSend NEXT to 22141 to receive details of the remaining {remaining} {remaining_term}"

            # Store messages
            incoming_message = Message(
                user_id=requesting_match.matched_user_id,
                message_direction="incoming",
                message_text=message
            )
            session.add(incoming_message)

            outgoing_message = Message(
                user_id=requesting_match.matched_user_id,
                message_direction="outgoing",
                message_text=response
            )
            session.add(outgoing_message)
            session.commit()
            return jsonify({"message": response}), 200

    except Exception as e:
        print(f"Error in next-matches: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/profile-details", methods=["POST"])
def request_profile():
    try:
        data = request.get_json()
        requester_phone = data.get("from")
        target_phone = data.get("message", "").strip()

        with get_session() as session:
            # Get requester details
            requester_match = session.query(Match).filter(
                Match.phone_number.like(f"%{requester_phone[-9:]}")
            ).first()
            if not requester_match:
                return jsonify({"message": "Please register first"}), 404

            requester = session.query(User).get(requester_match.matched_user_id)
            if not requester:
                return jsonify({"message": "User not found"}), 404

            # Store incoming message
            incoming_message = Message(
                user_id=requester.id,
                message_direction="incoming",
                message_text=target_phone
            )
            session.add(incoming_message)

            # Get target user details
            target_match = session.query(Match).filter(
                Match.phone_number.like(f"%{target_phone[-9:]}")
            ).first()

            if not target_match:
                error_msg = "User not found with that number"
                # Store error response
                outgoing_message = Message(
                    user_id=requester.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 404

            target_user = session.query(User).get(target_match.matched_user_id)
            if not target_user:
                error_msg = "User details not found"
                outgoing_message = Message(
                    user_id=requester.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 404

            # Get more details for target user
            target_more_details = session.query(UserMoreDetails).filter_by(user_id=target_user.id).first()
            if not target_more_details:
                error_msg = "User details not found"
                outgoing_message = Message(
                    user_id=requester.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 404

            # Ensure users are of opposite gender
            if target_user.gender == requester.gender:
                error_msg = "Invalid request. Please try another number."
                outgoing_message = Message(
                    user_id=requester.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 400

            # Message for requester
            requester_message = (
                f"{target_user.name} aged {target_user.age}, "
                f"{target_user.county} County, {target_user.town} town, "
                f"{target_more_details.level_of_education}, {target_more_details.profession}, "
                f"{target_more_details.marital_status}, {target_more_details.religion}, "
                f"{target_more_details.ethnicity}. "
                f"Send DESCRIBE {target_match.phone_number} to get more details about {target_user.name}."
            )

            # Store response message for requester
            outgoing_message = Message(
                user_id=requester.id,
                message_direction="outgoing",
                message_text=requester_message
            )
            session.add(outgoing_message)

            # Set gender-specific terms
            gender_term = "man" if requester.gender == "Male" else "woman"
            pronoun = "He" if requester.gender == "Male" else "She"
            pronoun_obj = "him" if requester.gender == "Male" else "her"

            # Notification message for target user
            notification_message = (
                f"Hi {target_user.name}, a {gender_term} called {requester.name} "
                f"is interested in you and requested your details.\n"
                f"{pronoun} is aged {requester.age} based in {requester.county}.\n"
                f"Do you want to know more about {pronoun_obj}? Send YES to 22141"
            )

            # Store notification message for target user
            notification_msg = Message(
                user_id=target_user.id,
                message_direction="outgoing",
                message_text=notification_message
            )
            session.add(notification_msg)

            session.commit()

            return jsonify({
                "message": requester_message,
                "notification": {
                    "to": target_match.phone_number,
                    "message": notification_message
                }
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/describe", methods=["POST"])
def get_description():
    try:
        data = request.get_json()
        requester_phone = data.get("from")
        message = data.get("message", "")

        with get_session() as session:
            # Find requesting user - handle different phone number formats
            requester_match = session.query(Match).filter(
                Match.phone_number.like(f"%{requester_phone[-9:]}")  # Match last 9 digits
            ).first()

            if not requester_match:
                return jsonify({"message": "Please register first"}), 404

            requester = session.query(User).get(requester_match.matched_user_id)

            # Store incoming message
            incoming_message = Message(
                user_id=requester.id,
                message_direction="incoming",
                message_text=message
            )
            session.add(incoming_message)

            # Check if message starts with DESCRIBE
            if not message.startswith("DESCRIBE"):
                error_msg = "Invalid format. Use: DESCRIBE phone_number"
                outgoing_message = Message(
                    user_id=requester.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 400

            # Extract phone number from message
            parts = message.split()
            if len(parts) != 2:
                error_msg = "Invalid format. Use: DESCRIBE phone_number"
                outgoing_message = Message(
                    user_id=requester.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 400

            target_phone = parts[1]

            # Find target user - handle different phone number formats
            target_match = session.query(Match).filter(
                Match.phone_number.like(f"%{target_phone[-9:]}")  # Match last 9 digits
            ).first()

            if not target_match:
                error_msg = "User not found"
                outgoing_message = Message(
                    user_id=requester.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 404

            target_user = session.query(User).get(target_match.matched_user_id)
                description = session.query(UserSelfDescription).filter_by(
                    user_id=target_user.id
                ).first()
            
            # Get description from UserSelfDescription table
            user_description = session.query(UserSelfDescription).filter_by(user_id=target_user.id).first()
            if not user_description:
                error_msg = "Description not found"
                outgoing_message = Message(
                    user_id=requester.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 404

                response = f"{target_user.name} describes {target_user.gender.lower()}self as {description.description}"
                store_message(session, user.id, "outgoing", response)
                session.commit()
            return jsonify({"message": response}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/confirm-interest", methods=["POST"])
def confirm_interest():
    try:
        with get_session() as session:
            # Find the user who was requested (the responder)
            responder_match = session.query(Match).filter(
                Match.phone_number.like(f"%{responder_phone[-9:]}")  # Match last 9 digits
            ).first()

            if not responder_match:
                return jsonify({"message": "User not found in matches"}), 404

            responder = session.query(User).get(responder_match.matched_user_id)

            # Store incoming YES message
            incoming_message = Message(
                user_id=responder.id,
                message_direction="incoming",
                message_text=message
            )
            session.add(incoming_message)

            if message.upper() != "YES":
                error_msg = "Invalid format. Please reply with YES"
                outgoing_message = Message(
                    user_id=responder.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 400

            # Find who requested their details (the requester)
            latest_request = session.query(MatchRequest).filter(
                MatchRequest.county == responder.county,
                MatchRequest.status == "pending"
            ).order_by(MatchRequest.id.desc()).first()

            if not latest_request:
                error_msg = "No pending requests found"
                outgoing_message = Message(
                    user_id=responder.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 404

            # Get the requester's details
            requester = session.query(User).get(latest_request.user_id)
            if not requester:
                error_msg = "Requester not found"
                outgoing_message = Message(
                    user_id=responder.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 404

            requester_match = session.query(Match).filter_by(matched_user_id=requester.id).first()
            if not requester_match:
                error_msg = "Requester match not found"
                outgoing_message = Message(
                    user_id=responder.id,
                    message_direction="outgoing",
                    message_text=error_msg
                )
                session.add(outgoing_message)
                session.commit()
                return jsonify({"message": error_msg}), 404

                if requester_details:
                    response += (
                        f"{requester_details.level_of_education}, {requester_details.profession}, "
                        f"{requester_details.marital_status}, {requester_details.religion}, "
                        f"{requester_details.ethnicity}."
                    )

            response = (
                f"{requester.name} aged {requester.age}, {requester.county} County, "
                f"{requester.town} town, {requester_details.level_of_education}, "
                f"{requester_details.profession}, {requester_details.marital_status}, "
                f"{requester_details.religion}, {requester_details.ethnicity}.\n"
                f"Send DESCRIBE {requester_match.phone_number} to get more details about {requester.name}"
            )

                store_message(session, user.id, "outgoing", response)
                session.commit()
            return jsonify({"message": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

