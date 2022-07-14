import React from 'react';
import { UseMutationResult } from 'react-query';
import {
    FieldValues,
    UseFormHandleSubmit,
    SubmitHandler,
} from 'react-hook-form';

import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';

import { Graph } from '../../calls';

const GraphCreate = <TFieldValues extends FieldValues = FieldValues>({
    mutation,
    useForm: { handleSubmit },
    fields,
}: {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    mutation: UseMutationResult<Graph, unknown, any>;
    useForm: {
        handleSubmit: UseFormHandleSubmit<TFieldValues>;
    };
    fields: TFieldValues;
}): JSX.Element => {
    const onSubmit: SubmitHandler<TFieldValues> = (data) => {
        mutation.mutate(data);
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
            </Container>{' '}
        </>
    );
};
export default GraphCreate;
