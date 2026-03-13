import React from 'react';
import { Button, ButtonProps, CircularProgress, Box } from '@mui/material';

type CustomButtonProps = ButtonProps & {
    loading?: boolean;
    loadingText?: string;
    containerProps?: React.ComponentProps<typeof Box>;
};

const CustomButton: React.FC<CustomButtonProps> = ({ 
    loading = false, 
    loadingText = 'Loading...', 
    children, 
    containerProps,
    ...props 
}) => {
    return (
        <Box 
            sx={{ gridColumn: 'span 12', display: 'flex', justifyContent: 'flex-end', ...containerProps?.sx }} 
            {...containerProps}
        >
            <Button 
                variant="contained" 
                color="primary" 
                size="large"
                disabled={loading || props.disabled}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : props.startIcon}
                {...props}
            >
                {loading ? loadingText : children}
            </Button>
        </Box>
    );
};

export default CustomButton;
