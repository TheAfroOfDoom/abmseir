import React from 'react';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';

import {
    CompleteGraphOptions,
    optionsCompleteGraph,
    postCompleteGraph,
} from '../../calls';
import GraphCreate from '.';

const GraphCreateComplete: React.FC = (): JSX.Element => {
    const queryClient = useQueryClient();
    const key = 'complete_graphs';
    const type = 'Complete';
    const mutation = useMutation(
        // TODO: convert these params to their specified types
        (params: { order: number }) => {
            console.log(`${typeof params.order}, ${params.order}`);
            return postCompleteGraph(params);
        },
        {
            mutationKey: key,
            onSuccess: () => {
                queryClient.invalidateQueries(key);
            },
            onError: (error) => {
                return;
            },
        }
    );
    const optionsQuery = useQuery<CompleteGraphOptions, Error>(
        `${key}_options`,
        optionsCompleteGraph
    );

    const { handleSubmit, control } =
        useForm<CompleteGraphOptions['actions']['POST']>();
    //     {
    //     defaultValues: {
    //         order: '',
    //     },
    // }

    return (
        <GraphCreate<CompleteGraphOptions['actions']['POST']>
            type={type}
            mutation={mutation}
            optionsQuery={optionsQuery}
            useForm={{
                handleSubmit: handleSubmit,
                control: control,
            }}
        />
    );
};
export default GraphCreateComplete;
