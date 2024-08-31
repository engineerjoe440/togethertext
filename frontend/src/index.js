import React from 'react';
import ReactDOM from 'react-dom';
import {RouterProvider, createBrowserRouter} from 'react-router-dom';
import { ThemeProvider } from '@mui/styles';
import ActivitySelect from "./ActivitySelect";
import HostWallMenu from './HostWallMenu';
import PlayerView from './PlayerView';
import theme from "./theme";
import './index.css';

const router = createBrowserRouter([
  {path: "/", element: <ActivitySelect />},
  {path: "/play/:hash", element: <ActivitySelect />},
  {path: "/host/:id", element: <HostWallMenu />},
  {path: "/review/:hash", element: <PlayerView />},
]);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <RouterProvider router={router} />
    </ThemeProvider>
  </React.StrictMode>,
);
