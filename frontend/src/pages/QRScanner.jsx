import { useEffect, useState }
    from "react";

import { Html5QrcodeScanner }
    from "html5-qrcode";

import jsQR from "jsqr";

import DashboardLayout
    from "../layouts/DashboardLayout";

import API from "../services/api";


function QRScanner() {

    const [result, setResult]
        = useState(null);

    const [loading, setLoading]
        = useState(false);


    // -----------------------------------
    // VERIFY QR
    // -----------------------------------

    const verifyQR =
        async (qrData) => {

            try {

                setLoading(true);

                const response =
                    await API.post(

                        "/api/qr/verify",

                        {
                            qr_data: qrData
                        }

                    );

                setResult(
                    response.data
                );

            }

            catch (error) {

                setResult({

                    status: "error",

                    message:
                        error.response?.data?.message
                        || "Verification failed"

                });

            }

            finally {

                setLoading(false);

            }

        };


    // -----------------------------------
    // CAMERA SCANNER
    // -----------------------------------

    useEffect(() => {

        const scanner =
            new Html5QrcodeScanner(

                "reader",

                {

                    fps: 10,

                    qrbox: {
                        width: 250,
                        height: 250
                    }

                },

                false

            );


        scanner.render(

            async (decodedText) => {

                await verifyQR(
                    decodedText
                );

            },

            (error) => {

                console.log(error);

            }

        );


        return () => {

            scanner.clear()
                .catch(error => {

                    console.log(error);

                });

        };

    }, []);


    // -----------------------------------
    // FILE UPLOAD
    // -----------------------------------

    const handleFileUpload =
        async (e) => {

            const file =
                e.target.files[0];

            if (!file) return;

            const image =
                new Image();

            const reader =
                new FileReader();

            reader.onload =
                (event) => {

                    image.src =
                        event.target.result;

                };

            image.onload =
                async () => {

                    const canvas =
                        document.createElement(
                            "canvas"
                        );

                    const ctx =
                        canvas.getContext("2d");

                    canvas.width =
                        image.width;

                    canvas.height =
                        image.height;

                    ctx.drawImage(
                        image,
                        0,
                        0
                    );

                    const imageData =
                        ctx.getImageData(

                            0,
                            0,
                            canvas.width,
                            canvas.height

                        );

                    const code =
                        jsQR(

                            imageData.data,

                            imageData.width,

                            imageData.height

                        );

                    if (code) {

                        await verifyQR(
                            code.data
                        );

                    }

                    else {

                        setResult({

                            status: "error",

                            message:
                                "No QR code detected"

                        });

                    }

                };

            reader.readAsDataURL(
                file
            );

        };


    return (

        <DashboardLayout>

            <h1 className="text-4xl font-bold mb-6">

                QR Scanner

            </h1>


            {/* CAMERA */}

            <div className="bg-white p-6 rounded-xl shadow mb-8">

                <h2 className="text-2xl font-bold mb-4">

                    Live Camera Scanner

                </h2>

                <div id="reader"></div>

            </div>


            {/* FILE UPLOAD */}

            <div className="bg-white p-6 rounded-xl shadow mb-8">

                <h2 className="text-2xl font-bold mb-4">

                    Upload QR Image

                </h2>

                <input

                    type="file"

                    accept="image/*"

                    onChange={handleFileUpload}

                />

            </div>


            {/* LOADING */}

            {
                loading && (

                    <p>

                        Verifying QR...

                    </p>

                )
            }


            {/* RESULT */}

            {
                result && (

                    <div className="bg-white p-6 rounded-xl shadow">

                        <h2 className="text-2xl font-bold mb-4">

                            Verification Result

                        </h2>

                        <p>

                            Status:
                            {" "}
                            <b>
                                {result.status}
                            </b>

                        </p>

                        <p>

                            Message:
                            {" "}
                            {result.message}

                        </p>

                    </div>

                )
            }

        </DashboardLayout>

    )

}

export default QRScanner;