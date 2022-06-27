import React from 'react';
import { useRoutes } from 'react-router-dom';

import { createTheme, ThemeProvider } from '@mui/material/styles';

import Header from './header/Header';
import errorRoutes from './error';
import graphRoutes from './graph';
import mainRoutes from './main';

// This extends the default theme with whatever specifications are desired
// https://mui.com/material-ui/customization/default-theme/
const theme = createTheme(createTheme(), {
    palette: {
        primary: {
            // TODO: set a sidebar color for dark mode
            // light:
            //     createTheme().palette.mode === 'light' ? '#bbdefb' : '#000000',
            light: '#bbdefb',
        },
    },
});

export const navBarPaths = [{ name: 'GRAPH', pathProps: { href: '/graph' } }];

const App: React.FC = (): JSX.Element => {
    const allRoutes = {
        path: '',
        element: <Header />,
        children: [errorRoutes, mainRoutes, graphRoutes],
    };

    const routing = useRoutes([allRoutes]);

    return <ThemeProvider theme={theme}>{routing}</ThemeProvider>;
};

export default App;
