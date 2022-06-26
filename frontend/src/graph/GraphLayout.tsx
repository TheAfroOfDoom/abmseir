import React from 'react';
import { Outlet } from 'react-router-dom';
import { Container } from '@mui/material';
import ListOutlinedIcon from '@mui/icons-material/ListOutlined';
import AddCircleOutlineOutlinedIcon from '@mui/icons-material/AddCircleOutlineOutlined';

import { ErrorFallback, SideBar } from '../util';

const GraphLayout: React.FC = (): JSX.Element => {
    const sideBarLinks = [
        {
            text: 'LIST',
            link: '/list',
            icon: <ListOutlinedIcon sx={{ color: 'primary.main' }} />,
        },
        {
            text: 'CREATE',
            link: '/create',
            icon: (
                <AddCircleOutlineOutlinedIcon sx={{ color: 'primary.main' }} />
            ),
        },
        {
            text: 'TEST',
            link: '/test',
            icon: (
                <AddCircleOutlineOutlinedIcon sx={{ color: 'primary.main' }} />
            ),
        },
    ];

    return (
        <>
            <SideBar
                aria-label="sidebar"
                baseUrl="/graph"
                sideBarLinks={sideBarLinks}
            />
            <Container sx={{ margin: 0, marginLeft: 0, padding: 0 }}>
                <ErrorFallback>
                    <Outlet />
                </ErrorFallback>
            </Container>
        </>
    );
};
export default GraphLayout;
