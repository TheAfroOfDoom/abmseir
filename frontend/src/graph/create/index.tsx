import React from 'react';
import { UseMutationResult } from 'react-query';
import {
    FieldValues,
    UseFormHandleSubmit,
    SubmitHandler,
} from 'react-hook-form';

import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Snackbar from '@mui/material/Snackbar';

import { Graph } from '../../calls';

interface ISnackbarData {
    visible: boolean;
    title: string;
    text: string;
    type: 'success' | 'error';
}

const GraphCreate = <TFieldValues extends FieldValues = FieldValues>({
    mutation,
    useForm: { handleSubmit },
    fields,
    snackbarData,
    setSnackbarData,
}: {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    mutation: UseMutationResult<Graph, unknown, any>;
    useForm: {
        handleSubmit: UseFormHandleSubmit<TFieldValues>;
    };
    fields: TFieldValues;
    snackbarData: ISnackbarData;
    setSnackbarData: any;
}): JSX.Element => {
    const onSubmit: SubmitHandler<TFieldValues> = (data) => {
        mutation.mutate(data);
    };

    const handleClose = (
        event?: React.SyntheticEvent | Event,
        reason?: string
    ) => {
        if (reason === 'clickaway') {
            return;
        }
        setSnackbarData({ ...snackbarData, visible: false });
    };

    return (
        <>
            <Grid key="graph-create-view-fields" container spacing={2}>
                {Object.entries(fields).map(([key, field]) => {
                    const Component = field.component;
                    return (
                        <Grid key={`graph-create-view-field-${key}`} item>
                            <Component />
                        </Grid>
                    );
                })}
            </Grid>
            <Container
                key="graph-create-view-submit"
                sx={{
                    display: 'flex',
                    justifyContent: 'flex-end',
                }}
            >
                <Button
                    variant="contained"
                    sx={{
                        m: 1,
                        mr: -2,
                    }}
                    onClick={handleSubmit(onSubmit)}
                >
                    Submit
                </Button>
            </Container>
            <Snackbar
                open={snackbarData.visible}
                autoHideDuration={6000}
                onClose={handleClose}
            >
                <Alert
                    variant="filled"
                    severity={snackbarData.type}
                    onClose={handleClose}
                >
                    <AlertTitle>{snackbarData.title}</AlertTitle>
                    {snackbarData.text}
                </Alert>
            </Snackbar>
        </>
    );
};
export default GraphCreate;
