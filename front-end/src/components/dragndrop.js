import React, { useState }  from 'react';
import axios from 'axios';
import Dropzone from 'react-dropzone';
import ProgressBar from 'react-bootstrap/ProgressBar';
import upload from '../images/upload.svg';
import { uploadFile } from '../api/upload';

const CancelToken = axios.CancelToken;
const source = CancelToken.source();

/**
 * Custom component that provides a nice drag and drop area for uploading
 * files to the server.
 * @param {function} uploadedCallback // Informs the parent that the file is uploaded
 * @param {function} uploadingCallback  // Informs the parent the file is being uploaded
 * @param {function} errorCallback // Informs the parent in case of network error
 */
const DragnDrop = ({ uploadedCallback, uploadingCallback, errorCallback }) => {
    const [progress, setProgress] = useState(0);

    /**
     * Send file to the parent so that it displays the file in the viewer.
     * @param {File[]} files 
     */
    const loadImage = (files) => {
        uploadingCallback(true, files);
    }

     /**
     * Called during inference by axios.
     * Keeps track of the progress and updates the percentage value
     * to be displayed in the prediction button.
     */
    const onUploadProgress = (progressEvent) => {
        const totalLength = progressEvent.lengthComputable ? progressEvent.total : progressEvent.target.getResponseHeader('content-length') || progressEvent.target.getResponseHeader('x-decompressed-content-length');
        if (totalLength !== null) {
            setProgress(Math.round( (progressEvent.loaded * 100) / totalLength ));
        }
    };

    /**
     * Parse the File object into a FormData ready for upload.
     * Uploads the image to the server and updates its state and its
     * parent's state.
     * Alert the parent in case of any network error.
     * @param {File} file 
     */
    const handleSend = (file) => {
        const data = new FormData();
        data.append('file', file);
        uploadFile(data, onUploadProgress, source.token).then(() => {
            uploadedCallback(true);
            uploadingCallback(false, null);
        }).catch(function (thrown) {
            if (axios.isCancel(thrown)) {
                console.log('Request canceled', thrown.message);
            } else {
                errorCallback();
            }
        });
    }

    const abortUpload = () => {
        source.cancel('Operation canceled by the user.');
    }

    return (
        <Dropzone
        accept={[".nii", ".nii.gz"]}
        onDrop={acceptedFiles => {  loadImage(acceptedFiles); handleSend(acceptedFiles[0]); }}
        multiple={false}>
            {({acceptedFiles, getRootProps, getInputProps}) => (
                <div {...getRootProps()} id="dragndrop" className={progress === 100 ? "upload-completed" : ""}>
                    <input data-testid='input'  {...getInputProps()} />
                    {acceptedFiles.length === 0 ? <img src={upload} height="50px" alt="upload" /> : null}
                    {acceptedFiles.length > 0
                    ? <p data-testid = 'progress'>
                        <strong>{acceptedFiles[0].path} </strong>
                        <span>{(progress < 100 ? " is being uploaded... " : " has been uploaded successfully. ")}</span>
                        <span><strong style={{ color: "#34a0d0" }}>Click</strong> to upload another file. </span>
                      </p>
                    : <p data-testid = 'drag' >Drag 'n' drop a Nifti file here, or <strong style={{ color: "#34a0d0" }}>click</strong> to select a file.</p>
                    }
                    {acceptedFiles.length > 0 && progress < 100 ? <ProgressBar className="mt-2" animated striped variant="info" label={`${progress}%`} now={progress} /> : null}
                </div>
            )}
        </Dropzone>
    );
}

export default DragnDrop;
