import React, { Fragment, useState, useEffect } from 'react';
import Card from 'react-bootstrap/Card';
import Spinner from 'react-bootstrap/Spinner';
import Button from 'react-bootstrap/Button';
import ListGroup from 'react-bootstrap/ListGroup';
import Badge from 'react-bootstrap/Badge';
import { getPrediction } from '../api/prediction';

/**
 * Score component that takes care of getting predictions and
 * retrieving the heat maps from the back-end.
 * @param {boolean} uploaded
 * @param {boolean} uploading
 * @param {function} callback
 */
const Score = ({ uploaded, uploading, callback }) => {
    const [isLoading, setLoading] = useState(false); // whether inference is being run
    const [score, setScore] = useState(null); // score value
    const [coords, setCoords] = useState({x: 0, y:0, z:0}); // current selected coordinates in viewer
    const [visitedCoords, setVisitedCoords] = useState([]); // list of visited coordinates
    const [showMaps, setShowMaps] = useState(true); // whether the user chooses to fetch the maps
    const [progress, setProgress] = useState(0); // download progress percentage

    /**
     * Called during inference by axios.
     * Keeps track of the progress and updates the percentage value
     * to be displayed in the prediction button.
     */
    const onDownloadProgress = (progressEvent) => {
        const totalLength = progressEvent.lengthComputable ? progressEvent.total : progressEvent.target.getResponseHeader('content-length') || progressEvent.target.getResponseHeader('x-decompressed-content-length');
        if (totalLength !== null) {
            setProgress(Math.round( (progressEvent.loaded * 100) / totalLength )); // Compute progress in percentage
        }
    };

    useEffect(() => {
        if (uploading) { // reset all attributes to initial values
            setCoords({x: 0, y:0, z:0});
            setVisitedCoords([]);
            setScore(null);
        }
    }, [uploading])

    useEffect(() => {
        if (isLoading) {
            console.log("Coords sent to backend :", coords)
            const askForMaps = showMaps;
            const viewer = window.papayaContainers[0].viewer;

            // Papaya coordinate shift due to different centers
            var center_y = Math.floor(viewer.volume.header.imageDimensions.yDim / 2);
            const origin_y = window.papayaContainers[0].viewer.volume.header.origin.y;
            var y = coords.y + 2 * (center_y - origin_y);
            getPrediction(coords.x, y, coords.z, onDownloadProgress, showMaps).then((res) => {
                console.log(res);
                setScore(res.headers.score); // get score from the response headers
                if (askForMaps) { // if the user asked for the maps, display them
                    callback(res.data);
                }
                setLoading(false); // stop the spinner
            }).catch(() => {
                setLoading(false);
                setScore('An error occured. Please try again later.')
            });
        }
    }, [isLoading]);

    /**
     * Triggered on click on the button
     * Sanity checks for the papaya container to be non empty
     * and retrieves the coordinates from the viewer.
     * Checks if the coordinates have never been visited: if so,
     * deletes the existing maps if any and set the loading attribute
     * to True.
     */
    const handleClick = () => {
        if (window.papayaContainers && window.papayaContainers.length > 0) {
            //  add new line
            const currentCoords = window.papayaContainers ? window.papayaContainers[0].viewer.currentCoord : {x: 0, y:0, z:0};
            const computedCoords = {
                x: currentCoords.x,
                y: currentCoords.y,
                z: currentCoords.z
            };
            const currentCoords_dummy = window.papayaContainers[0].viewer.getWorldCoordinateAtIndex(Number((currentCoords.x).toFixed(1)), Number((currentCoords.y).toFixed(1)), Number((currentCoords.z).toFixed(1)), new window.papaya.core.Coordinate(0, 0, 0));
            const computedCoords_dummy = {
                x: currentCoords_dummy.x,
                y: currentCoords_dummy.y,
                z: currentCoords_dummy.z
            };
            setCoords(computedCoords);

            console.log(computedCoords);
            console.log(visitedCoords);


            let coordsExist = false;
            visitedCoords.forEach((visitedCoord) => {
                coordsExist = JSON.stringify(visitedCoord[0]) === JSON.stringify(computedCoords_dummy);
            });
            if (!coordsExist) {
                setScore(null);
                if (visitedCoords.length > 0 && window.papayaContainers.length > 0 && window.papayaContainers[0].viewer.screenVolumes.length > 1) {
                    window.papaya.Container.removeImage(0, 1);
                }
                let temp = visitedCoords;
                temp.push([computedCoords_dummy, computedCoords]);
                setVisitedCoords(temp);
                setLoading(true);
                console.log(visitedCoords);
            }
        }
    }

    return (
        <Card className="box" style={{ backgroundColor: "white" }}>
            <Card.Body className="d-flex flex-column justify-content-between">
                <div className="d-flex justify-content-between">
                    <strong className="mb-3" style={{color: "black"}}>Inference</strong>
                    <label className="d-flex align-items-center w-50">
                        <input type="checkbox" checked={showMaps} onChange={() => setShowMaps(!showMaps)} />
                        <span title="Display attention maps" className="overflow-hidden text-truncate ml-1">Display attention maps</span>
                    </label>
                </div>
                <div>
                    <div className="d-flex justify-content-center">
                        <Card id="score">
                            <Card.Body className="d-flex flex-column align-items-center justify-content-center">
                                {isLoading ?
                                    <Spinner animation="border" role="status" variant="info">
                                        <span className="sr-only">Loading...</span>
                                    </Spinner>
                                :
                                    <Fragment>
                                        <Card.Title className="text-center">
                                            <h1>Score</h1>
                                        </Card.Title>
                                        <h4 style={{ color: "#f34949", textAlign: "center", fontSize: "1.2em" }}>{score}</h4>
                                    </Fragment>
                                }
                            </Card.Body>
                        </Card>
                    </div>
                    <Button
                        bg="dark"
                        variant="dark"
                        className="my-3"
                        data-testid='button'
                        style={{ borderRadius: "4px", color: "#35a0d0", backgroundColor: "transparent", border: "2px solid #35a0d0", width: "70%", marginLeft: "15%" }}
                        disabled={isLoading || uploading}
                        onClick={!isLoading ? handleClick : null}>
                        <strong>{isLoading ? 'Predicting...' + progress + '%' : (uploading ? 'Waiting for image...' : (uploaded ? 'Get prediction' : 'No image'))}</strong>
                    </Button>
                    {visitedCoords.length > 0 ?
                    <Card>
                        <Card.Body>
                            <Card.Title>
                                <h1>Coordinates</h1>
                            </Card.Title>
                            <ListGroup>
                                {visitedCoords.slice().reverse().map((coordinates, idx) => (
                                    <ListGroup.Item key={idx} action onClick={() => window.papayaContainers[0].viewer.gotoCoordinate(coordinates[1])}>
                                        <div className="d-flex justify-content-between">
                                            <Badge variant="info" className="d-flex align-items-center">Coords {visitedCoords.length - idx}</Badge>
                                            <span data-testid="X">X: {Number((coordinates[0].x).toFixed(1))}</span>
                                            <span data-testid="Y">Y: {Number((coordinates[0].y).toFixed(1))}</span>
                                            <span data-testid="Z">Z: {Number((coordinates[0].z).toFixed(1))}</span>
                                        </div>
                                    </ListGroup.Item>
                                ))}
                            </ListGroup>
                        </Card.Body>
                    </Card> : null}
                </div>
            </Card.Body>
        </Card>
    )
};

export default Score;
