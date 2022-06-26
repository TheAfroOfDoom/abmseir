import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Container } from '@mui/material';

import { ErrorFallback } from '../util';
import NavBar from './navbar/NavBar';

const Header: React.FC = (): JSX.Element => {
    const headerElements = (
        <>
            <NavBar />
        </>
    );

    return (
        <>
            <Box
                sx={{
                    bgcolor: 'primary.light',
                    height: '100vh',
                    display: 'flex',
                    flexDirection: 'column',
                }}
            >
                {headerElements}
                <Container
                    maxWidth="xl"
                    sx={{
                        backgroundColor: 'primary.contrastText',
                        display: 'flex',
                        flexDirection: 'row',
                        flex: 1,
                        paddingLeft: 0,
                    }}
                >
                    <ErrorFallback>
                        <Outlet />
                    </ErrorFallback>
                </Container>
            </Box>
        </>
    );
};
export default Header;
