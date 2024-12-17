import React, { useEffect } from "react";
import Alert from '@mui/material/Alert';
import IconButton from '@mui/material/IconButton';
import Collapse from '@mui/material/Collapse';
import CloseIcon from '@mui/icons-material/Close';

function AlertComponent({ open, setOpen, message, mode }) {
    useEffect(() => {
        const timer = setTimeout(() => {
            setOpen(false);
        }, 5000);

        return () => clearTimeout(timer);
    }, [open, setOpen]);

    const alertStyle = {
        margin: '10px auto', // Выравнивание по центру
        textAlign: 'center', // Выравнивание текста по центру
    };

    return (
        <Collapse in={open}>
            <Alert
                style={alertStyle}
                severity={mode}
                action={
                    <IconButton
                        aria-label="close"
                        color="inherit"
                        size="small"
                        onClick={() => {
                            setOpen(false);
                        }}
                    >
                        <CloseIcon fontSize="inherit" />
                    </IconButton>
                }
            >
                <strong>{message}</strong>
            </Alert>
        </Collapse>
    );
}

export default AlertComponent;
