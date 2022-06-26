import React from 'react';
import { Card, CardMedia } from '@mui/material';

const MainView: React.FC = (): JSX.Element => {
    return (
        <>
            <Card
                variant="outlined"
                sx={{
                    p: 1,
                    display: 'flex',
                    flexDirection: { xs: 'column', sm: 'row' },
                    justifyContent: 'center',
                }}
            >
                <CardMedia
                    component="img"
                    alt="sweet baby oola dog"
                    image={process.env.PUBLIC_URL + '/images/oola.jpg'}
                    sx={{
                        borderRadius: 0.5,
                        width: '400px',
                        maxWidth: '50%',
                    }}
                />
            </Card>
        </>
    );
};
export default MainView;
