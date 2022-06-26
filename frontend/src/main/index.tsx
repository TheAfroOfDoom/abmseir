import MainLayout from './MainLayout';
import MainView from './MainView';

const routes = {
    path: '',
    element: <MainLayout />,
    children: [{ index: true, element: <MainView /> }],
};
export default routes;
