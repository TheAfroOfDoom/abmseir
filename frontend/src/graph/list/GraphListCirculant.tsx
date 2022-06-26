import React from 'react';
import { useQuery } from 'react-query';

import { getCirculantGraph, getCirculantGraphs } from '../../calls';
import GraphList from '.';

const GraphListCirculant: React.FC = (): JSX.Element => {
    const key = 'circulant_graphs';
    const type = 'Circulant';
    const columns = ['ID', 'Order', 'Jumps'];
    const query = useQuery(key, getCirculantGraphs);
    const dataQueryProps = { key: key, func: getCirculantGraph };

    return (
        <GraphList
            type={type}
            columns={columns}
            query={query}
            dataQueryProps={dataQueryProps}
        />
    );
};
export default GraphListCirculant;
