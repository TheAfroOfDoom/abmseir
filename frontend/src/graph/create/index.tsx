import React from 'react';
import { UseMutationResult, UseQueryResult } from 'react-query';
import {
    Control,
    Controller,
    FieldPath,
    FieldValues,
    UseFormHandleSubmit,
    SubmitHandler,
} from 'react-hook-form';

import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';

import { Graph, GraphOptions } from '../../calls';

const GraphCreate = <TFieldValues extends FieldValues = FieldValues>({
    type,
    mutation,
    optionsQuery,
    useForm: { handleSubmit, control },
}: {
    type: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    mutation: UseMutationResult<Graph, unknown, any>;
    optionsQuery: UseQueryResult<GraphOptions, Error>;
    useForm: {
        handleSubmit: UseFormHandleSubmit<GraphOptions['actions']['POST']>;
        control: Control<TFieldValues>;
    };
}): JSX.Element => {
    if (optionsQuery.isLoading) {
        return <CircularProgress />;
    }
    if (optionsQuery.isError || optionsQuery.data === undefined) {
        throw new Error('Failed to fetch options query data');
    }
    const fields = optionsQuery.data.actions.POST;

    const onSubmit: SubmitHandler<NonNullable<typeof fields>> = (data) => {
        // console.log(data);
        mutation.mutate(data);
    };

    // TODO: figure out defaultValues weirdness with generics to remove console error on value change
    // const defaultValues: Record<keyof typeof fields, ''> = {};
    // Object.keys(fields).forEach((field) => {
    //     const _field = field as keyof typeof fields;
    //     defaultValues[_field] = '';
    // });
    // const defaultValues: Record<string, ''> = {};
    // Object.keys(fields).forEach((field) => {
    //     defaultValues[field] = '';
    // });

    return (
        <>
            <Grid key="graph-create-view-fields" container spacing={2}>
                {Object.entries(fields)
                    .filter(([key, field]) => field.read_only === false)
                    .map(([key, field]) => {
                        const _key = key as FieldPath<TFieldValues>;
                        return (
                            <Grid key={`graph-create-view-field-${key}`} item>
                                <Controller
                                    name={_key}
                                    control={control}
                                    render={({
                                        field: { onChange, value },
                                    }) => (
                                        <TextField
                                            onChange={onChange}
                                            value={value}
                                            label={field.label}
                                            id={`field-${key}`}
                                            // variant="filled"
                                        />
                                    )}
                                />
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
