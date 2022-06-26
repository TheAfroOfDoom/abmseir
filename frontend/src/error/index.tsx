import { Navigate, Outlet } from 'react-router-dom';

import PageNotFound from './PageNotFound';

const routes = {
    path: '',
    element: <Outlet />,
    children: [
        { path: '*', element: <Navigate to="404" /> },
        { path: '404', element: <PageNotFound /> },
    ],
};
export default routes;
