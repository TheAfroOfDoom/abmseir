import { Method } from 'axios';

export interface PaginatedResponse {
    count: number;
    next: null;
    previous: null;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    results: Array<any>; // this interface should never be used directly by actual data
}

export interface FieldRequiredProps {
    type: string;
    required: boolean;
    read_only: boolean;
    label: string;
}

export interface Field extends FieldRequiredProps {
    min_value?: number;
    max_value?: number;
    min?: number;
    max?: number;
}

export interface Options {
    name: string;
    description: string;
    renders: string[];
    parses: string[];
    actions?: Record<Method, Record<string, Field>>;
}

const formatField = (
    field: Field,
    oldProperty: keyof typeof field,
    newProperty: keyof typeof field
): Field => {
    let newField: Field = { ...field };

    if (oldProperty in field) {
        // newField[newProperty] = field[oldProperty];
        newField = { ...field, [newProperty]: field[oldProperty] };
        delete newField[oldProperty];
        return newField;
    }
    return field;
};

export const formatOptions = (options: Options): Options => {
    const actions = options.actions;
    if (actions === undefined) {
        return options;
    }

    Object.entries(actions).forEach(([_key, action]) => {
        const action_key = _key as Method;
        Object.keys(action).forEach((field_key) => {
            actions[action_key][field_key] = formatField(
                actions[action_key][field_key],
                'min_value',
                'min'
            );
            actions[action_key][field_key] = formatField(
                actions[action_key][field_key],
                'max_value',
                'max'
            );
        });
    });
    return options;
};
