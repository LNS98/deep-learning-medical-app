import React, { useState } from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

const RGPDModal = () => {
    const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);

    return (
        <Modal show={show} onHide={handleClose} centered>
            <Modal.Header closeButton>
                <Modal.Title>RGPD stuff</Modal.Title>
            </Modal.Header>
            <Modal.Body>Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
                sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
                Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris 
                nisi ut aliquip ex ea commodo consequat.</Modal.Body>
            <Modal.Footer>
                <Button variant="primary" onClick={handleClose}>
                    I agree
                </Button>
            </Modal.Footer>
      </Modal>)
};

export default RGPDModal;