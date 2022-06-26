import React from 'react';
import { Container, Box, Typography } from '@mui/material';

const PageNotFound: React.FC = (): JSX.Element => {
    return (
        <Container>
            <Box
                sx={{
                    background: '#F3D9C0',
                    border: 3,
                    borderRadius: 2,
                    py: '50px',
                    my: 4,
                }}
            >
                <Typography
                    variant="h4"
                    sx={{
                        color: 'red',
                        textAlign: 'center',
                        fontWeight: 'bold',
                    }}
                >
                    Error 404: Page not found
                </Typography>
            </Box>
        </Container>
    );
};
export default PageNotFound;
