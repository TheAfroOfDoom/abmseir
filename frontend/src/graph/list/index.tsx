import React from 'react';
import { UseQueryResult } from 'react-query';

import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';

import { Graph } from '../../calls';
import { PaginatedResponse } from '../../calls/common';
import GraphRender from './GraphRender';

const GraphList: React.FC<{
    type: string;
    columns: string[];
    query: UseQueryResult<PaginatedResponse>;
    dataQueryProps: {
        key: string;
        func: (id: string) => Promise<Graph & { data: Blob }>;
    };
}> = ({ type, columns, query, dataQueryProps }): JSX.Element => {
    if (query.isLoading) {
        return <CircularProgress />;
    }
    if (query.isError || query.data === undefined) {
        throw new Error(
            `GraphList query for type ${type} returned undefined data`
        );
    }
    const graphs = query.data.results;

    return (
        <Paper>
            <Typography variant="h5" component="h2" sx={{ p: 1 }}>
                {type}
            </Typography>
            <Divider light />
            <React.Suspense fallback={<CircularProgress />}>
                <TableContainer sx={{ margin: 0, marginLeft: 0, padding: 0 }}>
                    <Table sx={{ minWidth: 650 }} aria-label={`${type}-list`}>
                        <TableHead>
                            <TableRow>
                                {columns.map((column) => (
                                    <TableCell
                                        key={`graph-list-${type}-head-column-${column}`}
                                        scope="col"
                                    >
                                        {column}
                                    </TableCell>
                                ))}
                                <TableCell // View/render button
                                    key={`graph-list-${type}-head-column-view`}
                                    scope="col"
                                />
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {graphs.map((graph) => (
                                <TableRow
                                    key={graph.id}
                                    sx={{
                                        '&:last-child td, &:last-child th': {
                                            border: 0,
                                        },
                                    }}
                                >
                                    {Object.entries(graph).map(
                                        ([key, value]) => {
                                            if (key === 'id') {
                                                return (
                                                    <TableCell
                                                        key={`${graph.id}-${key}`}
                                                        component="th"
                                                        scope="row"
                                                    >
                                                        {String(value)}
                                                    </TableCell>
                                                );
                                            } else if (Array.isArray(value)) {
                                                return (
                                                    <TableCell
                                                        key={`${graph.id}-${key}`}
                                                    >
                                                        {`{${value.join(
                                                            ', '
                                                        )}}`}
                                                    </TableCell>
                                                );
                                            }
                                            return (
                                                <TableCell
                                                    key={`${graph.id}-${key}`}
                                                >
                                                    {String(value)}
                                                </TableCell>
                                            );
                                        }
                                    )}
                                    <TableCell key={`${graph.id}-render`}>
                                        <GraphRender
                                            id={graph.id}
                                            queryProps={dataQueryProps}
                                        />
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </React.Suspense>
        </Paper>
    );
};
export default GraphList;
