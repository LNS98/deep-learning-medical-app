import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import Footer from '../components/footer.js';

test('if the footer image is shown', async () => {
  const {getByTestId} = render(<Footer />);

  expect(getByTestId('footer')).not.toBeNull()
}
)
