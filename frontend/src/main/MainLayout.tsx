import React from 'react';
import { Outlet } from 'react-router-dom';
import { Container, Typography } from '@mui/material';

const MainLayout: React.FC = (): JSX.Element => (
    <>
        <Container
            sx={{
                display: 'block',
            }}
        >
            <Typography variant="h2" sx={{ textAlign: 'center' }}>
                This is the main module :)
            </Typography>
            <Outlet />
        </Container>
    </>
);
export default MainLayout;
