import React, { useState } from 'react';
import LoadingOverlay from 'react-loading-overlay';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Alert from 'react-bootstrap/Alert';
import DragNDrop  from './dragndrop';
import Score from './score';
import Infos from './infos';
import Box from './box';
import upload from '../images/upload_white.svg';
import metrics from '../images/metrics.png';


/**
 * Main component for displaying the center component of the app.
 * Wraps the Infos, DragNDrop, Score component and the papaya viewer
 */
const Visualization = () => {
    const [uploading, setUploading] = useState(false); // whether an image is being uploaded
    const [uploaded, setUploaded] = useState(false); // whether an image has been uploaded
    const [error, setError] = useState(null); // if any error occurs during download/upload

    /**
     * Triggers uploading process to the back-end
     * If a file has been selected, the papaya viewer is reset and the selected
     * image is loaded into it.
     * After 2 seconds, the coordinate system is changed to physical (matches with
     * model specifications).
     * @param {bool} uploading
     * @param {File[]} files
     */
    const uploadingCallback = (uploading, files) => {
        setUploading(uploading);
        if (files) {
            window.papaya.Container.resetViewer(0);
            window.papayaContainers[0].toolbar.doAction("OpenImage", files, true);
            //setTimeout(() => window.papayaContainers[0].viewer.toggleWorldSpace(), 2000);
        }
    }

    /**
     * Creates a Blob from the heat maps data received from the back-end (as string)
     * and load them into the viewer (stacks them on top of the loaded image)
     * @param {string} data
     */
    const dowloadingFeatureMapsCallback = (data) => {
        var blob = new Blob([data]);
        blob.lastModifiedDate = new Date();
        blob.name = "feature-maps";
        window.papayaContainers[0].toolbar.doAction("OpenImage", [blob], true);
    }

    const errorCallback = () => setError('An error occured. Please try again later.');

    return (
    <Container id="visu" className="py-5 px-5 h-90" style={{ maxWidth: "100%" }}>
        {error ? <Alert variant="danger">{error}</Alert> : null}
        <Row className="mb-5 row-flex">
            <Col sm={8} className="h-100">
                <Infos />
            </Col>
            <Col sm={4} className="h-100">
                <Box color="white" title="Upload image">
                    <DragNDrop uploadedCallback={setUploaded} uploadingCallback={uploadingCallback} errorCallback={errorCallback} />
                    <img src={metrics} style={{ maxWidth: "100%", height: "auto" }} className="mt-3" alt="metrics" />
                </Box>
            </Col>
        </Row>
        <Row className="row-flex">
            <Col sm={!uploaded && !uploading ? 12 : 8}>
                <Box color="black" title="Papaya Viewer" >
                    <LoadingOverlay
                        active={!uploaded && !uploading}
                        spinner={false}
                        text={
                            <div className="d-flex flex-column align-items-center" data-testid='papaya_window' >
                                <img src={upload} alt="upload" height="50px" width="60px" />
                                <span>Please upload an image first</span>
                            </div>
                        }
                        >
                            <div className="papaya" data-params="params"></div>{/* data-params="params" */}
                    </LoadingOverlay>
                </Box>
            </Col>
            <Col sm={uploading || uploaded ? 4 : 0} className={!uploaded && !uploading ? "score-hidden" : "score mt-4 mt-sm-0"}>
                <Score uploaded={uploaded} uploading={uploading} callback={dowloadingFeatureMapsCallback} />
            </Col>
        </Row>
    </Container>);
};

export default Visualization;
