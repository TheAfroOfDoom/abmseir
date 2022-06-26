import React, { createElement, useState } from 'react';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
// import Divider from '@mui/material/Divider';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Paper from '@mui/material/Paper';
import Select from '@mui/material/Select';
import Typography from '@mui/material/Typography';

import GraphCreateCirculant from './GraphCreateCirculant';
import GraphCreateComplete from './GraphCreateComplete';

const graphTypes = {
    complete_graph: {
        label: 'Complete',
        component: GraphCreateComplete,
    },
    circulant_graph: {
        label: 'Circulant',
        component: GraphCreateCirculant,
    },
};

const GraphCreateView: React.FC<{ graphType?: keyof typeof graphTypes }> = (
    props
): JSX.Element => {
    const [graphType, setGraphType] = useState<keyof typeof graphTypes | ''>(
        props.graphType || ''
    );

    return (
        <>
            <Paper
                key="graph-create-view-paper"
                sx={{
                    border: 1,
                    mt: 2,
                    mb: 2,
                    p: 1,
                }}
            >
                <Typography
                    variant="h4"
                    component="h1"
                    sx={{ textAlign: 'center', p: 2 }}
                >
                    Create Graph
                </Typography>
            </Paper>
            <FormControl fullWidth>
                <InputLabel id="graph-type-select-label">Type</InputLabel>
                <Select
                    labelId="graph-type-select-label"
                    id="graph-type-select"
                    value={graphType}
                    label="Type"
                    onChange={(event) => {
                        const newValue = event.target
                            .value as keyof typeof graphTypes;
                        if (newValue in graphTypes && newValue !== graphType) {
                            setGraphType(newValue);
                        }
                    }}
                >
                    {Object.entries(graphTypes).map(([key, value]) => (
                        <MenuItem
                            key={`graph-create-view-dropdown-${key}`}
                            value={key}
                        >
                            {value.label}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            {graphType && (
                <Box>
                    <React.Suspense fallback={<CircularProgress />}>
                        <Paper
                            key="graph-create-view-paper-fields"
                            sx={{
                                // border: 1,
                                mt: 2,
                                mb: 2,
                                p: 1,
                            }}
                        >
                            {createElement(graphTypes[graphType].component)}
                        </Paper>
                    </React.Suspense>
                </Box>
            )}
        </>
    );
};
export default GraphCreateView;
