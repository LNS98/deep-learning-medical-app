import React from 'react';
import { render, fireEvent, waitForElement } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import Visualization from '../components/visu';

jest.mock('axios');

test('clicks and checks if upload is not disabled', async () => {
    const { getByRole, getByClass, getByTestId } = render(<Visualization />);

    expect(getByTestId('papaya_window')).toHaveTextContent('Please upload an image first')
    //Mock a picture to upload
    // const file = new File(['mri_scan'], 'patient_zero.nii', {
    //   type: 'image/nii',
    // })
    //
    // //expect(getByTestId('upload-button')).toHaveAttribute('disabled');
    //
    // Object.defineProperty(getByTestId('visu'), 'files', {
    //   value: [file]
    // })
    //
    // fireEvent.change(getByTestId('input'));
    //
    // expect(getByTestId('upload-button')).not.toHaveAttribute('disabled');

})
