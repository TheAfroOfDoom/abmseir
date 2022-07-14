import React from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { Controller, useForm, FieldValues } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import { postCompleteGraph } from '../../calls';
import GraphCreate from '.';

interface ISnackbarData {
    visible: boolean;
    title: string;
    text: string;
    type: 'success' | 'error';
}

const GraphCreateComplete: React.FC = (): JSX.Element => {
    const [snackbarData, setSnackbarData] = React.useState<ISnackbarData>({
        visible: false,
        title: '',
        text: '',
        type: 'error',
    });

    const queryClient = useQueryClient();
    const key = 'complete_graphs';
    const mutation = useMutation(
        (params: { order: number }) => postCompleteGraph(params),
        {
            mutationKey: key,
            onSuccess: () => {
                queryClient.invalidateQueries(key);
            },
            onSettled: (data, error: any) => {
                if (error) {
                    setSnackbarData({
                        visible: true,
                        title: 'Error generating new Complete Graph',
                        text: error.response.data[0],
                        type: 'error',
                    });
                } else {
                    setSnackbarData({
                        visible: true,
                        title: 'Complete Graph generated',
                        text: '',
                        type: 'success',
                    });
                }
            },
        }
    );

    const schema = z.object({
        order: z
            .number()
            .int()
            .min(1)
            .max(2 ** 31 - 1),
    });

    const defaultValues = {
        order: '',
    };

    const { handleSubmit, control } = useForm<typeof fields>({
        defaultValues: defaultValues,
        resolver: zodResolver(schema),
    });

    const OrderTextField = () => (
        <Box>
            <Typography>Order</Typography>
            <Controller
                name={'order'}
                control={control}
                render={({
                    field: { onChange, value },
                    fieldState: { isDirty, error },
                }) => (
                    <TextField
                        id={`field-${key}`}
                        value={value}
                        sx={{ pt: 1 }}
                        error={error && !isDirty}
                        label={error?.message}
                        onChange={(e) =>
                            onChange(
                                !isNaN(parseInt(e.target.value))
                                    ? parseInt(e.target.value)
                                    : e.target.value
                            )
                        }
                    />
                )}
            />
        </Box>
    );

    const fields: FieldValues = {
        order: {
            label: 'Order',
            type: 'number',
            component: OrderTextField,
        },
    };

    return (
        <GraphCreate<typeof fields>
            mutation={mutation}
            useForm={{ handleSubmit: handleSubmit }}
            fields={fields}
            snackbarData={snackbarData}
            setSnackbarData={setSnackbarData}
        />
    );
};
export default GraphCreateComplete;
