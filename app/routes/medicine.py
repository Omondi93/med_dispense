from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.medicine import Medicine


medicine_bp = Blueprint(
    "medicine",
    __name__,
    url_prefix="/api/medicine"
)


# -----------------------------------
# CREATE MEDICINE
# -----------------------------------

@medicine_bp.route("/", methods=["POST"])
@jwt_required()
def create_medicine():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "No JSON data received"
            }), 400


        name = data.get("name")

        if not name:

            return jsonify({
                "success": False,
                "error": "Medicine name required"
            }), 400


        # Logged in manufacturer
        manufacturer_id = int(
            get_jwt_identity()
        )


        medicine = Medicine(

            name=name,

            manufacturer_id=manufacturer_id

        )


        db.session.add(medicine)

        db.session.commit()


        return jsonify({

            "success": True,
            "message": "Medicine created successfully",
            "medicine_id": medicine.id

        }), 201


    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,
            "error": str(e)

        }), 500


# -----------------------------------
# GET ALL MEDICINES
# -----------------------------------

@medicine_bp.route("/", methods=["GET"])
@jwt_required()
def get_medicines():

    try:

        medicines = Medicine.query.all()

        results = []

        for medicine in medicines:

            results.append({

                "id": medicine.id,

                "name": medicine.name,

                "manufacturer_id":
                medicine.manufacturer_id

            })


        return jsonify({

            "success": True,

            "data": results

        }), 200


    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500