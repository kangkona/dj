import { Formik, Form, Field, ErrorMessage, useFormikContext } from 'formik';
import CodeMirror from '@uiw/react-codemirror';
import { langs } from '@uiw/codemirror-extensions-langs';

import NamespaceHeader from '../../components/NamespaceHeader';
import Select, { Options } from 'react-select';
import { useField } from 'formik';
import { useContext, useEffect, useRef, useState } from 'react';
import DJClientContext from '../../providers/djclient';
import 'styles/node-creation.scss';
import InvalidIcon from "../../icons/InvalidIcon";
import AlertIcon from "../../icons/AlertIcon";

const FormikSelect = ({
  selectOptions,
  formikFieldName,
  placeholder,
  style,
}) => {
  // eslint-disable-next-line no-unused-vars
  const [field, _, helpers] = useField(formikFieldName);
  const { setValue } = helpers;

  return (
    <Select
      className="SelectInput"
      defaultValue={selectOptions.find(option => option.value === field.value)}
      options={selectOptions}
      placeholder={placeholder}
      onBlur={field.onBlur}
      onChange={option => setValue(option.value)}
      styles={style}
    />
  );
};
FormikSelect.defaultProps = {
  placeholder: '',
};

const NodeQuery = ({ djClient }) => {
  const [schema, setSchema] = useState([]);
  const formik = useFormikContext();

  useEffect(() => {
    const fetchData = async () => {
      const nodes = await djClient.namespace('source');
      const schema = {};
      console.log('nodes', nodes);
      for (const node of nodes) {
        const nodeDetails = await djClient.node(node.name);
        schema[node.name] = nodeDetails.columns.map(col => col.name);
      }
      setSchema(schema);
    };
    fetchData().catch(console.error);
  }, [djClient, djClient.namespace]);

  return (
    <>
      <Field
        type="textarea"
        style={{ display: 'none' }}
        as="textarea"
        name="query"
      />
      <div role="button" tabIndex={0} className="relative flex bg-[#282a36]">
        <CodeMirror
          id={'query'}
          name={'query'}
          extensions={[
            langs.sql({
              schema: schema,
            }),
          ]}
          options={{
            theme: 'default',
            lineNumbers: true,
          }}
          width="100%"
          height="400px"
          style={{
            margin: '0 0 23px 0',
            flex: 1,
            fontSize: '150%',
            textAlign: 'left',
          }}
          onChange={val => {
            formik.setFieldValue('query', val);
          }}
        />
      </div>
    </>
  );
};

const FullNameField = props => {
  const { values, touched, setFieldValue } = useFormikContext();
  const [field, meta] = useField(props);

  useEffect(() => {
    // set the value of textC, based on textA and textB
    console.log('values', values);
    if (values.namespace && values.display_name) {
      setFieldValue(
        props.name,
        values.namespace +
          '.' +
          values.display_name.toLowerCase().replace(/ /g, '_'),
      );
    }
  }, [setFieldValue, props.name, values]);

  return (
    <>
      <input {...props} {...field} className="FullNameField" />
      {!!meta.touched && !!meta.error && <div>{meta.error}</div>}
    </>
  );
};

export function CreateNodePage({ props }) {
  const djClient = useContext(DJClientContext).DataJunctionAPI;
  const [namespaces, setNamespaces] = useState([]);
  const formik = useFormikContext();
  const [code, setCode] = useState('');
  const [error, setError] = useState('');

  const createNode = async (values, setStatus) => {
    const data = {};
    data.name = values.name;
    data.display_name = values.display_name;
    data.description = values.description;
    data.query = values.query;
    data.mode = values.mode;
    data.namespace = values.namespace;

    const response = await fetch(
      `${process.env.REACT_APP_DJ_URL}/nodes/${values.node_type}/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        credentials: 'include',
      },
    ).catch(error => {
      setError(error ? JSON.stringify(error) : '');
    });
    const responseMessage = await response.json();
    if (response.status === 200 || response.status === 201) {
      setStatus({
        success: `Created node <a href="/nodes/${responseMessage.name}">${responseMessage.name}</a>`,
      });
    } else {
      setStatus({
        success: `${responseMessage.message}`,
      });
    }
  };

  // Get namespaces
  useEffect(() => {
    const fetchData = async () => {
      const namespaces = await djClient.namespaces();
      setNamespaces(
        namespaces.map(m => ({ value: m['namespace'], label: m['namespace'] })),
      );
    };
    fetchData().catch(console.error);
  }, [djClient, djClient.metrics]);

  return (
    <div className="mid">
      <NamespaceHeader namespace="" />
      <div className="card">
        <div className="card-header">
          <h2>Create Node</h2>
          <center>
            <Formik
              initialValues={{
                name: '',
                display_name: '',
                query: '',
                node_type: '',
                description: '',
                mode: 'draft',
              }}
              validate={values => {
                const errors = {};
                if (!values.name) {
                  errors.name = 'Required';
                }
                if (!values.query) {
                  errors.query = 'Required';
                }
                return errors;
              }}
              onSubmit={(values, { setSubmitting, setStatus }) => {
                setTimeout(() => {
                  createNode(values, setStatus);
                  setSubmitting(false);
                }, 400);
              }}
            >
              {({ isSubmitting, status }) => (
                <Form>
                  {status?.success !== undefined ? (
                    <div className="alert">
                      <AlertIcon />
                      {status?.success}
                    </div>
                  ) : (
                    ''
                  )}
                  <div className="NodeTypeInput NodeCreationInput">
                    <ErrorMessage name="node_type" component="span" />
                    <label>Node Type</label>
                    <Field as="select" name="node_type">
                      <option value=""></option>
                      <option value="dimension">Dimension</option>
                      <option value="transform">Transform</option>
                      <option value="metric">Metric</option>
                    </Field>
                  </div>
                  <div className="NamespaceInput">
                    <ErrorMessage name="namespace" component="span" />
                    <label>Namespace</label>
                    <FormikSelect
                      selectOptions={namespaces}
                      formikFieldName="namespace"
                      placeholder="Choose Namespace"
                    />
                  </div>
                  <div className="DisplayNameInput NodeCreationInput">
                    <ErrorMessage name="display_name" component="span" />
                    <label>Display Name</label>
                    <Field type="text" name="display_name" />
                  </div>
                  <div className="FullNameInput NodeCreationInput">
                    <ErrorMessage name="name" component="span" />
                    <label>Full Name</label>
                    <FullNameField type="text" name="name" />
                  </div>
                  <div className="DescriptionInput NodeCreationInput">
                    <ErrorMessage name="description" component="span" />
                    <label>Description:</label>
                    <Field
                      type="textarea"
                      as="textarea"
                      name="description"
                      placeholder="Describe your node"
                    />
                  </div>
                  <div className="QueryInput NodeCreationInput">
                    <ErrorMessage name="query" component="span" />
                    <label>Query</label>
                    <NodeQuery djClient={djClient} />
                  </div>
                  <div className="NodeModeInput NodeCreationInput">
                    <ErrorMessage name="mode" component="span" />
                    <label>Mode</label>
                    <Field as="select" name="mode">
                      <option value="draft">Draft</option>
                      <option value="published">Published</option>
                    </Field>
                  </div>
                  <button type="submit" disabled={isSubmitting}>
                    Create
                  </button>
                </Form>
              )}
            </Formik>
          </center>
        </div>
      </div>
    </div>
  );
}
