import { useContext, useState } from 'react';
import * as React from 'react';
import DJClientContext from '../../providers/djclient';
import { ErrorMessage, Field, Form, Formik } from 'formik';
import { FormikSelect } from '../AddEditNodePage/FormikSelect';
import EditIcon from '../../icons/EditIcon';
import { displayMessageAfterSubmit, labelize } from '../../../utils/form';

export default function AddNamespacePopover({ namespace, onSubmit }) {
  const djClient = useContext(DJClientContext).DataJunctionAPI;
  const [popoverAnchor, setPopoverAnchor] = useState(false);

  const addNamespace = async ({ namespace }, { setSubmitting, setStatus }) => {
    setSubmitting(false);
    const response = await djClient.addNamespace(namespace);
    if (response.status === 200 || response.status === 201) {
      setStatus({ success: 'Saved' });
    } else {
      setStatus({
        failure: `${response.json.message}`,
      });
    }
    onSubmit();
    window.location.reload();
  };

  return (
    <>
      <button
        className="edit_button"
        aria-label="AddNamespaceTogglePopover"
        tabIndex="0"
        onClick={() => {
          setPopoverAnchor(!popoverAnchor);
        }}
      >
        <EditIcon />
      </button>
      <div
        className="popover"
        role="dialog"
        aria-label="AddNamespacePopover"
        style={{
          display: popoverAnchor === false ? 'none' : 'block',
          width: '200px !important',
          textTransform: 'none',
          fontWeight: 'normal',
        }}
      >
        <Formik
          initialValues={{
            namespace: '',
          }}
          onSubmit={addNamespace}
        >
          {function Render({ isSubmitting, status, setFieldValue }) {
            return (
              <Form>
                {displayMessageAfterSubmit(status)}
                <span data-testid="add-namespace">
                  <ErrorMessage name="namespace" component="span" />
                  <label htmlFor="namespace">Namespace</label>
                  <Field
                    type="text"
                    name="namespace"
                    id="namespace"
                    placeholder="New namespace"
                  />
                </span>
                <button
                  className="add_node"
                  type="submit"
                  aria-label="SaveNamespace"
                  aria-hidden="false"
                  style={{ marginTop: '1rem' }}
                >
                  Save
                </button>
              </Form>
            );
          }}
        </Formik>
      </div>
    </>
  );
}
