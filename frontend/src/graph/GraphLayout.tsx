import React from 'react';
import { Outlet } from 'react-router-dom';
import { Container } from '@mui/material';

import { ErrorFallback, SideBar } from '../util';

const GraphLayout: React.FC<{
    sideBarPaths: {
        text: string;
        path: string;
        element: JSX.Element;
        icon: JSX.Element;
    }[];
}> = ({ sideBarPaths }): JSX.Element => {
    return (
        <>
            <SideBar
                aria-label="sidebar"
                baseUrl="/graph"
                sideBarPaths={sideBarPaths}
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
