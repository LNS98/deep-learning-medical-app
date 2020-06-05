import React from 'react';
import Card from 'react-bootstrap/Card';

/**
 * Higher Order Component that wraps up components into
 * a rounded white responsive box.
 * @param {func} children // React components to wrap
 * @param {string} color // Color of the title
 * @param {string} title // Title of the box
 */
const Box = ({ children, color, title}) => {
    return (
        <Card className="box" style={{ backgroundColor: color }}>
            <Card.Body className="d-flex flex-column justify-content-between">
                <div className="d-flex justify-content-between">
                    <strong className="mb-3" style={{color: color === "black" ? "white" : ""}}>{title}</strong>
                </div>
                {children}
            </Card.Body>
        </Card>
    );
}

export default Box;