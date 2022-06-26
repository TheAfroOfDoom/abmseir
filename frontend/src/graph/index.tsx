import { Navigate } from 'react-router-dom';

import GraphLayout from './GraphLayout';
import GraphListView from './list/GraphListView';
import GraphCreateView from './create/GraphCreateView';

const routes = {
    path: 'graph',
    element: <GraphLayout />,
    children: [
        { index: true, element: <Navigate to="list" /> },
        { path: 'list', element: <GraphListView /> },
        { path: 'create', element: <GraphCreateView /> },
    ],
};
export default routes;
