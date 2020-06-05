import React from 'react';
import {act, fireEvent, render} from '@testing-library/react';
import DragnDrop  from '../components/dragndrop';
import Dropzone from 'react-dropzone';

const file = new File(['mri_scan'], "minimal.nii", {
  type: 'image/nii',
});

test('if it sets {accept} prop on the <input>', () => {
      const accept = 'image/nii'
      const { container } = render(
        <Dropzone accept={accept}>
          {({ getRootProps, getInputProps }) => (
            <div {...getRootProps()}>
              <input {...getInputProps()} />
            </div>
          )}
        </Dropzone>
      );

      const input = container.querySelector('input');

      expect(input).toHaveAttribute('accept', file.type);
    })

test('if it drops an image', async () => {

    const data = mockData([file]);
    const onDrop = jest.fn();

    const ui = (
      <Dropzone onDrop={onDrop}>
        {({ getRootProps, getInputProps }) => (
          <div {...getRootProps()}>
            <input {...getInputProps()} />
          </div>
        )}
      </Dropzone>
    );
    const { container } = render(ui);
    const dropzone = container.querySelector('div');

    dispatchEvt(dropzone, 'drop', data);
    await flushPromises(ui, container);

    expect(onDrop).toHaveBeenCalled();
})

test('if it does nt set {multiple} prop on the <input>', () => {
      const { container } = render(
        <Dropzone multiple = {false} >
          {({ getRootProps, getInputProps }) => (
            <div {...getRootProps()}>
              <input {...getInputProps()} />
            </div>
          )}
        </Dropzone>
      )

      const input = container.querySelector('input')
      expect(input).not.toHaveAttribute('multiple')
    })

function flushPromises(ui, container) {
  return new Promise(resolve =>
    setImmediate(() => {
      render(ui, { container })
      resolve(container)
    })
  );
}

function dispatchEvt(node, type, data) {
  const event = new Event(type, { bubbles: true });
  Object.assign(event, data);
  fireEvent(node, event);
}

function mockData(files) {
  return {
    dataTransfer: {
      files,
      items: files.map(file => ({
        kind: 'file',
        type: file.type,
        getAsFile: () => file
      })),
      types: ['Files']
    }
  };
}
