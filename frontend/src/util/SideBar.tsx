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
    sideBarLinks: {
        text: string;
        link: string;
        icon: JSX.Element;
    }[];
}> = ({ baseUrl, sideBarLinks }): JSX.Element => {
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
                {sideBarLinks.map((sideBarLink) => (
                    <Link
                        key={sideBarLink.text}
                        color="inherit"
                        underline="none"
                        href={`${baseUrl}${sideBarLink.link}`}
                    >
                        <ListItem key={sideBarLink.text} disablePadding>
                            <ListItemButton
                                sx={{ paddingLeft: 3, paddingRight: 3 }}
                            >
                                <ListItemIcon
                                    sx={{
                                        minWidth: 'auto',
                                        paddingRight: 2,
                                    }}
                                >
                                    {sideBarLink.icon}
                                </ListItemIcon>
                                <ListItemText primary={sideBarLink.text} />
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
