import React from 'react';
import { 
    Box, 
    FormControl, 
    InputLabel, 
    Select, 
    MenuItem, 
    OutlinedInput 
} from '@mui/material';

type CustomTextFieldProps = {
    name: string;
    label: string;
    type?: string;
    defaultValue?: string | number;
    gridSpan?: number;
    options?: { value: string | number; label: string }[];
    inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
    onChange?: (value: string) => void;
};

const CustomTextField: React.FC<CustomTextFieldProps> = ({ 
    name,
    label,
    type = 'text',
    defaultValue,
    gridSpan = 4, 
    options,
    inputProps,
    onChange,
}) => {
    return (
        <Box sx={{ gridColumn: { xs: 'span 12', sm: `span ${gridSpan}` } }}>
            <FormControl fullWidth variant="outlined">
                <InputLabel id={`${name}-label`}>{label}</InputLabel>
                {options ? (
                    <Select
                        labelId={`${name}-label`}
                        name={name}
                        defaultValue={defaultValue ?? options[0].value}
                        label={label}
                        input={<OutlinedInput label={label} />}
                        onChange={onChange ? (e) => onChange(String(e.target.value)) : undefined}
                    >
                        {options.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.label}
                            </MenuItem>
                        ))}
                    </Select>
                ) : (
                    <OutlinedInput
                        name={name}
                        type={type}
                        defaultValue={defaultValue}
                        label={label}
                        inputProps={inputProps}
                        onChange={onChange ? (e) => onChange(e.target.value) : undefined}
                    />
                )}
            </FormControl>
        </Box>
    );
};

export default CustomTextField;
