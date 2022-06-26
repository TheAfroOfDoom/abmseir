import React from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { amber } from '@mui/material/colors';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';

export const ErrorContainer: React.FC<{ error: Error }> = ({
    error,
}): JSX.Element => {
    return (
        <Container
            sx={{
                backgroundColor: amber[50],
                border: 3,
                borderColor: 'secondary.light',
                p: 2,
            }}
        >
            <Typography
                variant="h4"
                component="h1"
                sx={{ color: 'error.main' }}
            >
                {`${error}`}
            </Typography>
            <Divider sx={{ m: 1 }} />
            <Container sx={{ p: 2 }}>
                {error.stack ? (
                    <>
                        <Typography
                            variant="h5"
                            component="h2"
                            sx={{ color: 'error.light' }}
                        >
                            Stack trace:
                        </Typography>
                        <Typography
                            variant="body1"
                            component="h3"
                            sx={{
                                color: 'error.light',
                                whiteSpace: 'pre-line',
                            }}
                            display="inline"
                        >
                            {error.stack}
                        </Typography>
                    </>
                ) : (
                    <Typography
                        variant="h5"
                        component="h2"
                        sx={{ color: 'error.light' }}
                    >
                        No stack trace available.
                    </Typography>
                )}
            </Container>
        </Container>
    );
};

export const ErrorFallback: React.FC<{ children?: JSX.Element }> = ({
    children,
}): JSX.Element => (
    <ErrorBoundary
        FallbackComponent={({ error }) => <ErrorContainer error={error} />}
    >
        {children}
    </ErrorBoundary>
);
export default ErrorFallback;
