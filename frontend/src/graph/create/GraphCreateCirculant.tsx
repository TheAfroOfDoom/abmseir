import React from 'react';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';

import {
    CirculantGraphOptions,
    optionsCirculantGraph,
    postCirculantGraph,
} from '../../calls';
import GraphCreate from '.';

const GraphCreateCirculant: React.FC = (): JSX.Element => {
    const queryClient = useQueryClient();
    const key = 'circulant_graphs';
    const type = 'Circulant';
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
    const optionsQuery = useQuery<CirculantGraphOptions, Error>(
        `${key}_options`,
        optionsCirculantGraph
    );
    const { handleSubmit, control } =
        useForm<NonNullable<CirculantGraphOptions['actions']['POST']>>();

    return (
        <GraphCreate<CirculantGraphOptions['actions']['POST']>
            type={type}
            mutation={mutation}
            optionsQuery={optionsQuery}
            useForm={{ handleSubmit: handleSubmit, control: control }}
        />
    );
};
export default GraphCreateCirculant;
