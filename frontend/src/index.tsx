import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
// import reportWebVitals from './reportWebVitals';

import { ErrorFallback } from './util';
import App from './App';

export const API_URL = process.env.REACT_APP_API_URL;

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            // suspense: true,
        },
    },
});

const element = (
    <React.StrictMode>
        <BrowserRouter>
            <QueryClientProvider client={queryClient}>
                <ErrorFallback>
                    <App />
                </ErrorFallback>
                <ReactQueryDevtools />
            </QueryClientProvider>
        </BrowserRouter>
    </React.StrictMode>
);

const container = document.getElementById('root');
if (container === null) throw new Error('Root container missing in index.html');

const root = createRoot(container);
root.render(element);

// TODO
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// reportWebVitals();
