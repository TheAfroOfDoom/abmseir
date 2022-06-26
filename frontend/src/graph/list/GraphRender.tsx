// TODO: see if this cytoscape react package is better than `react-cytoscapejs`
// https://www.npmjs.com/package/cytoscape-react
import React, { useState } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import CytoscapeComponent from 'react-cytoscapejs';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import IconButton from '@mui/material/IconButton';
import { styled } from '@mui/material/styles';

import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import CloseIcon from '@mui/icons-material/Close';

import { Graph } from '../../calls';
import { CytoscapeStyled, ErrorFallback } from '../../util';

const BootstrapDialog = styled(Dialog)(({ theme }) => ({
    '& .MuiDialogContent-root': {
        padding: theme.spacing(2),
    },
    '& .MuiDialogActions-root': {
        padding: theme.spacing(1),
    },
}));

export interface DialogTitleProps {
    id: string;
    children?: React.ReactNode;
    onClose: () => void;
}

const BootstrapDialogTitle = (props: DialogTitleProps) => {
    const { children, onClose, ...other } = props;

    return (
        <DialogTitle sx={{ m: 0, p: 2 }} {...other}>
            {children}
            {onClose ? (
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    sx={{
                        position: 'absolute',
                        right: 8,
                        top: 8,
                        color: (theme) => theme.palette.grey[500],
                    }}
                >
                    <CloseIcon />
                </IconButton>
            ) : null}
        </DialogTitle>
    );
};

const GraphLayout: React.FC<{
    data: Blob | undefined;
}> = ({ data }): JSX.Element => {
    return (
        <CytoscapeStyled
            elements={CytoscapeComponent.normalizeElements(
                JSON.parse(
                    // atob(String(data))
                    // Buffer.from(data, 'base64').toString()
                    window.atob(String(data))
                ).elements
            )}
        />
    );
};

const GraphRender: React.FC<{
    id: string;
    queryProps: {
        key: string;
        func: (id: string) => Promise<Graph & { data: Blob }>;
    };
}> = ({ id, queryProps }): JSX.Element => {
    const [open, setOpen] = useState(false);
    const query = useQuery(
        [queryProps.key, { id }],
        () => queryProps.func(id),
        {
            enabled: false,
            suspense: false,
        }
    );
    const queryClient = useQueryClient();
    const handleClickOpen = () => {
        setOpen(true);
        query.refetch();
    };
    const handleClose = () => {
        setOpen(false);
        queryClient.cancelQueries(queryProps.key);
    };

    return (
        <>
            <Button onClick={handleClickOpen}>
                <VisibilityOutlinedIcon />
            </Button>
            <BootstrapDialog
                onClose={handleClose}
                aria-labelledby="customized-dialog-title"
                open={open}
            >
                <BootstrapDialogTitle
                    id="customized-dialog-title"
                    onClose={handleClose}
                >
                    Render graph
                </BootstrapDialogTitle>
                <DialogContent
                    dividers
                    sx={{ width: '600px', height: '600px' }}
                >
                    <ErrorFallback>
                        {query.isLoading ? (
                            <CircularProgress />
                        ) : (
                            <GraphLayout data={query.data?.data} />
                        )}
                    </ErrorFallback>
                </DialogContent>
                <DialogActions>
                    <Button autoFocus onClick={handleClose}>
                        Close
                    </Button>
                </DialogActions>
            </BootstrapDialog>
        </>
    );
};
export default GraphRender;
