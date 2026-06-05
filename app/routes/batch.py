from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from datetime import datetime

from app import db

from app.models.batch import Batch
from app.models.medicine import Medicine


batch_bp = Blueprint(

    "batch",

    __name__,

    url_prefix="/api/batch"

)


# -----------------------------------
# CREATE BATCH
# -----------------------------------

@batch_bp.route("/", methods=["POST"])
@jwt_required()
def create_batch():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,
                "error": "No JSON data"

            }), 400


        medicine_id = data.get(
            "medicine_id"
        )

        batch_number = data.get(
            "batch_number"
        )

        manufacture_date = data.get(
            "manufacture_date"
        )

        expiry_date = data.get(
            "expiry_date"
        )

        quantity = data.get(
            "quantity"
        )


        # Validation

        if not all([

            medicine_id,
            batch_number,
            manufacture_date,
            expiry_date,
            quantity

        ]):

            return jsonify({

                "success": False,
                "error": "All fields required"

            }), 400


        # Verify medicine exists

        medicine = db.session.get(
            Medicine,
            medicine_id
        )

        if not medicine:

            return jsonify({

                "success": False,
                "error": "Medicine not found"

            }), 404


        # Logged in manufacturer

        manufacturer_id = int(
            get_jwt_identity()
        )


        batch = Batch(

            batch_number=batch_number,

            medicine_id=medicine_id,

            manufacturer_id=manufacturer_id,

            manufacture_date=datetime.strptime(
                manufacture_date,
                "%Y-%m-%d"
            ),

            expiry_date=datetime.strptime(
                expiry_date,
                "%Y-%m-%d"
            ),

            quantity=int(quantity)

        )


        db.session.add(batch)

        db.session.commit()


        return jsonify({

            "success": True,

            "message": "Batch created successfully",

            "batch_id": batch.id

        }), 201


    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# -----------------------------------
# GET BATCHES
# -----------------------------------

@batch_bp.route("/", methods=["GET"])
@jwt_required()
def get_batches():

    try:

        batches = Batch.query.all()

        results = []

        for batch in batches:

            results.append({

                "id": batch.id,

                "batch_number":
                batch.batch_number,

                "medicine_id":
                batch.medicine_id,

                "medicine_name": batch.medicine.name if batch.medicine else None,

                "quantity":
                batch.quantity,

                "manufacture_date": batch.manufacture_date.isoformat(),

                "expiry_date":
                batch.expiry_date.isoformat()

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