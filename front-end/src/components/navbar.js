import React from 'react';
import Navbar from 'react-bootstrap/Navbar';

/**
 * Simple title bar placed at the top of the app.
 */
const NavBar = () => (
    <Navbar className="navigation py-3" style={{ backgroundColor: "#173D4E" }} expand="lg">
        <Navbar.Brand data-testid="navbar" style={{ fontSize: "4vh" }} color="white" href="#home" className="pl-5 text-white">Tackling Crohns disease using Deep Learning</Navbar.Brand>
        <div className="names pr-5 text-white text-truncate">
            <span>Lorenzo Niccolini, Yoanna Peneva, Toby Godwin</span>
            <span>Charles Metz, George Yiasemis, Ahmed Djermani</span>
            <span>supervised by <a href="http://wp.doc.ic.ac.uk/bkainz/">Bernhard Kainz</a></span>
            <span>original model by <a href="https://arxiv.org/abs/1909.00276">Robert Holland</a></span>
        </div>
    </Navbar>
);

export default NavBar;
