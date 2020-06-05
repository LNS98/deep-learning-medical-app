import React from 'react';
import mockAxios from 'jest-mock-axios';
import UppercaseProxy from './UppercaseProxy';
import { cleanup, render, fireEvent, waitForElement } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import Score from '../components/score';
//import { SERVER_BASE_URL } from '../constants/api';

afterEach(cleanup)


test('if displays proper message when uploading', async () => {
    const { getByRole } = render(<Score uploading={true}/>);

    expect(getByRole('button')).toHaveAttribute('disabled');
    expect(getByRole('button')).toHaveTextContent('Waiting for image...');

})


test('if displays proper message when image is uploaded', async () => {
    const { getByRole } = render(<Score uploaded={true}/>);

    expect(getByRole('button')).not.toHaveAttribute('disabled');
    expect(getByRole('button')).toHaveTextContent('Get prediction');

})

test('clicks and receives score', async () => {
    const { getByRole, queryByRole, queryByText, getByTestId } = render(<Score isLoading={true} callback={null}/>);
    window.papayaContainers = [{viewer:{currentCoord : {x: 0, y:0, z:0}}}]
    // console.log(getByRole('button'))
    fireEvent.click(getByTestId('button'));
    // console.log(getByRole('button'))
    expect(getByTestId('button')).toHaveAttribute('disabled');
    expect(getByTestId('button')).toHaveTextContent('Predicting...');
    // Check if there is a spinner
    expect(queryByRole('status')).not.toBe(null);
    expect(queryByText('Score')).toBeNull();

    // Check if coordinates are visible
    const [x_coord, y_coord, z_coord] =  [
        getByTestId('X'),
        getByTestId('Y'),
        getByTestId('Z'),
      ]

    expect(x_coord).toHaveTextContent('X: 0');
    expect(y_coord).toHaveTextContent('Y: 0');
    expect(z_coord).toHaveTextContent('Z: 0');
})

test('if it displays nothing', async () => {
    const { getByRole } = render(<Score uploaded={false}/>);

    // expect(getByRole('button')).toHaveAttribute('disabled');
    expect(getByRole('button')).toHaveTextContent('No image');

})
