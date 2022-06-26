import { Field, FieldRequiredProps, Options } from '../common';

export interface Graph {
    id: string;
    order: number;
}

export interface GraphOptions extends Options {
    actions: {
        POST: {
            id: FieldRequiredProps;
            order: FieldRequiredProps;
        } & Record<string, Field>;
    } & Options['actions'];
}
