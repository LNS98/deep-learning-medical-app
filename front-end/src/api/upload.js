import axios from 'axios';

import { SERVER_BASE_URL } from '../constants/api';

export const uploadFile = (data, onUploadProgress, cancelToken) => axios.post(SERVER_BASE_URL + "upload", data, {onUploadProgress}, {cancelToken}, { // receive two parameter endpoint url ,form data 
    })
    .then(res => { // then print response status
    console.log(res.statusText)
    })