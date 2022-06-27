import { Navigate } from 'react-router-dom';

import ListOutlinedIcon from '@mui/icons-material/ListOutlined';
import AddCircleOutlineOutlinedIcon from '@mui/icons-material/AddCircleOutlineOutlined';

import GraphLayout from './GraphLayout';
import GraphListView from './list/GraphListView';
import GraphCreateView from './create/GraphCreateView';

const defaultRoute = 'list';
const paths = [
    {
        text: 'LIST',
        path: 'list',
        element: <GraphListView />,
        icon: <ListOutlinedIcon sx={{ color: 'primary.main' }} />,
    },
    {
        text: 'CREATE',
        path: 'create',
        element: <GraphCreateView />,
        icon: <AddCircleOutlineOutlinedIcon sx={{ color: 'primary.main' }} />,
    },
];

const routes = {
    path: 'graph',
    element: <GraphLayout sideBarPaths={paths} />,
    children: [
        { index: true, element: <Navigate to={defaultRoute} /> },
        ...paths,
    ],
};
export default routes;
