import React from 'react';
import { render, fireEvent, waitForElement } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import NavBar from '../components/navbar';

test('if title is shown in navbar', async () => {
  const {getByTestId} = render(<NavBar />);
  const title = "Tackling Crohn's disease using Deep Learning"
  
  expect(getByTestId('navbar')).toHaveTextContent(title)
}
)
