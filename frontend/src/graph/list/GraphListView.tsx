import React from 'react';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import GraphListCirculant from './GraphListCirculant';
import GraphListComplete from './GraphListComplete';

const graphLists: React.FC[] = [GraphListCirculant, GraphListComplete];
const GraphListView: React.FC = (): JSX.Element => {
    return (
        <>
            <Paper
                key="graph-list-view-paper"
                sx={{
                    border: 1,
                    // borderColor: 'theme.mode' == 'light' ? 'grey.500' : 'grey.',
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
                    Generated Graphs
                </Typography>
            </Paper>
            <Stack divider={<Divider />} spacing={2}>
                {graphLists.map((GraphList, index) => (
                    <GraphList key={GraphList.name} />
                ))}
            </Stack>
        </>
    );
};
export default GraphListView;
