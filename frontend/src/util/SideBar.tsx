import React from 'react';

import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';

export const SideBar: React.FC<{
    baseUrl: string;
    sideBarPaths: {
        text: string;
        path: string;
        icon: JSX.Element;
    }[];
}> = ({ baseUrl, sideBarPaths }): JSX.Element => {
    return (
        <Box
            sx={{
                borderRight: 4,
                borderColor: 'divider',
                display: 'flex',
                flex: 1,
                marginLeft: '-24px',
                maxWidth: 'fit-content',
            }}
        >
            <List>
                {sideBarPaths.map((sideBarPath) => (
                    <Link
                        key={sideBarPath.text}
                        color="inherit"
                        underline="none"
                        href={`${baseUrl}/${sideBarPath.path}`}
                    >
                        <ListItem key={sideBarPath.text} disablePadding>
                            <ListItemButton
                                sx={{ paddingLeft: 3, paddingRight: 3 }}
                            >
                                <ListItemIcon
                                    sx={{
                                        minWidth: 'auto',
                                        paddingRight: 2,
                                    }}
                                >
                                    {sideBarPath.icon}
                                </ListItemIcon>
                                <ListItemText primary={sideBarPath.text} />
                            </ListItemButton>
                        </ListItem>
                    </Link>
                ))}
            </List>
            <Divider />
        </Box>
    );
};
export default SideBar;
