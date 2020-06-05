import React from 'react';
import { FaRegCheckCircle } from 'react-icons/fa';

// List of instructions to explain the web app functionalities.
const instructions = [
    "Click on the upload button and choose an image to upload, or drag and drop an image into the Upload Image box. ",
    "Explore the file in Papaya viewer and select the coordinates where the terminal ileum is. ",
    "Once the image is uploaded, click on 'Get Prediction' which will query the model and return a score.",
    "Tick the box labelled 'Display attention maps' to return an overlay of the salient features considered by the model. Note, this will slow down predictions by ~3 minutes.",
    "As an assessment of the model’s performance, metrics are displayed below the drag'n'drop area.",
    "NOTE: Do not click outside of the body. No prediction will be returned.",
    "NOTE: To adjust the transparency of the salient features, click on the colourful square at the top right hand corner of the Papaya viewer. There will be a transparency scroll, which adjusts the transparency of the overlay."
];

const Infos = () => {
    return (
        <div id="infos" className="text-left">
            <h1>How to use the application:</h1>
            {instructions.map((instr, idx) => (
                <div key={idx} className="d-flex align-items-top mb-2">
                    <div><FaRegCheckCircle className="mr-2" /></div>
                    {instr}
                </div>
            ))}
            <p>
                <strong>Additional information: </strong>
                The web-page queries the model built by Holland et al. <a href="https://arxiv.org/pdf/1909.00276.pdf">https://arxiv.org/pdf/1909.00276.pdf</a>
            </p>
        </div>
    );
};

export default Infos;
