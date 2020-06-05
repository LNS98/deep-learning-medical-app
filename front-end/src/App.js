import React, { Fragment } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import NavBar from './components/navbar';
import Visualization from './components/visu';
import RGPDModal from './components/rgpd_modal';
import Footer from './components/footer';

/**
 * Main wrapper of the web application
 * The app is composed of 3 components:
 * - NavBar
 * - Visualisation panel
 * - Footer
 */
function App() {
    return (
        <Fragment>
            <NavBar />
            <Visualization />
            {/*<RGPDModal />*/}
            <Footer />
        </Fragment>
    );
}

export default App;
