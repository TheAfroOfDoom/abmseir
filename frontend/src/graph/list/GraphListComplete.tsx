import React from 'react';
import { useQuery } from 'react-query';

import { getCompleteGraph, getCompleteGraphs } from '../../calls';
import GraphList from '.';

const GraphListComplete: React.FC = (): JSX.Element => {
    const key = 'complete_graphs';
    const type = 'Complete';
    const columns = ['ID', 'Order'];
    const query = useQuery(key, getCompleteGraphs);
    const dataQueryProps = { key: key, func: getCompleteGraph };

    return (
        <GraphList
            type={type}
            columns={columns}
            query={query}
            dataQueryProps={dataQueryProps}
        />
    );
};
export default GraphListComplete;
