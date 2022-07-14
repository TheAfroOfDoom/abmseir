import React from 'react';
import { useMutation, useQueryClient } from 'react-query';
import {
    Controller,
    useFieldArray,
    useForm,
    FieldValues,
} from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';

import { postCirculantGraph } from '../../calls';
import GraphCreate from '.';

const GraphCreateCirculant: React.FC = (): JSX.Element => {
    const queryClient = useQueryClient();
    const key = 'circulant_graphs';
    const mutation = useMutation(
        (params: { order: number; jumps: number[] }) =>
            postCirculantGraph(params),
        {
            mutationKey: key,
            onSuccess: () => {
                queryClient.invalidateQueries(key);
            },
        }
    );

    const schema = z.object({
        order: z
            .number()
            .int()
            .min(1)
            .max(2 ** 31 - 1),
        jumps: z
            .array(
                z
                    .number()
                    .int()
                    .min(1)
                    .max(2 ** 31 - 1)
            )
            .nonempty(),
    });
    // .refine((data) => {
    //     jumps.forEach((jump) => )
    // });

    const defaultValues = {
        order: '',
        jumps: [1], // TODO: this should be `''` but it doesn't show up
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

    const {
        fields: jumps,
        append,
        remove,
    } = useFieldArray({
        control,
        name: 'jumps',
    });
    // TODO: sort jumps on onChange
    // const sortJumps = () => {
    //     jumps.forEach((jump) => {
    //         console.log(jump);
    //     });
    //     jumps.sort();
    // };
    const JumpArrayField = () => {
        return (
            <Box>
                <Typography>Jumps</Typography>
                <List sx={{ pt: 0 }}>
                    {jumps.map((jump, index) => (
                        <ListItem key={jump.id} disableGutters>
                            <Controller
                                name={`jumps.${index}`}
                                control={control}
                                render={({
                                    field: { onChange, value },
                                    fieldState: { isDirty, error },
                                }) => (
                                    <TextField
                                        id={`jumps.${index}`}
                                        value={value}
                                        error={error && !isDirty}
                                        label={error?.message}
                                        onChange={(e) => {
                                            const parsedJump = onChange(
                                                !isNaN(parseInt(e.target.value))
                                                    ? parseInt(e.target.value)
                                                    : e.target.value
                                            );

                                            // sortJumps();

                                            return parsedJump;
                                        }}
                                    />
                                )}
                            />
                        </ListItem>
                    ))}
                </List>
                <Container>
                    <Button
                        aria-label="add-jump"
                        variant="outlined"
                        onClick={() => {
                            append(defaultValues.jumps[0]);
                        }}
                    >
                        <AddIcon />
                    </Button>
                    <Button
                        aria-label="remove-jump"
                        variant="outlined"
                        onClick={() => {
                            if (jumps.length > 1) {
                                remove(jumps.length - 1);
                            }
                        }}
                    >
                        <RemoveIcon />
                    </Button>
                </Container>
            </Box>
        );
    };

    const fields: FieldValues = {
        order: {
            label: 'Order',
            type: 'number',
            component: OrderTextField,
        },
        jumps: {
            label: 'Jumps',
            component: JumpArrayField,
        },
    };

    return (
        <GraphCreate<typeof fields>
            mutation={mutation}
            useForm={{ handleSubmit: handleSubmit }}
            fields={fields}
        />
    );
};
export default GraphCreateCirculant;
