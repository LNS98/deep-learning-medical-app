import React, { Fragment } from 'react';
import Jumbotron from 'react-bootstrap/Jumbotron';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import imperial from '../images/IC.svg';

/**
 * Simple footer at the bottom of the app.
 */
const Footer = () => (
    <Fragment>
        <hr className="m-0" />
        <Jumbotron fluid className="mb-0 px-5 text-white d-flex align-items-center" style={{ backgroundColor: "#F7F7F7", height: "18vh" }}>
            <Container className="d-flex flex-column" style={{ maxWidth: "100%" }}>
                <Row>
                    <Col sm={4}>
                        <img data-testid='footer' alt="" src={imperial} height="100%" />
                    </Col>
                </Row>
            </Container>
        </Jumbotron>
    </Fragment>
);

export default Footer;
