import axios, { AxiosRequestConfig } from 'axios';

import { API_URL } from '../..';
import { Field, formatOptions, PaginatedResponse } from '../common';
import { GraphOptions, Graph } from './common';

const CIRCULANT_GRAPH_URL = '/graphs/circulant';

interface CirculantGraph extends Graph {
    jumps: number[];
}

interface CirculantGraphResults extends Omit<PaginatedResponse, 'results'> {
    results: CirculantGraph[];
}

export interface CirculantGraphOptions extends GraphOptions {
    actions: {
        POST: {
            jumps: Field;
        } & GraphOptions['actions']['POST'];
    } & GraphOptions['actions'];
}

// TODO: Merge these into a single call that will fetch graph data if id param is specified
export const getCirculantGraphs = (): Promise<CirculantGraphResults> =>
    axios
        .get(`${API_URL}${CIRCULANT_GRAPH_URL}`)
        .then((response) => response.data);

export const getCirculantGraph = (
    id: string,
    signal?: AxiosRequestConfig['signal']
): Promise<CirculantGraph & { data: Blob }> =>
    axios
        .get(`${API_URL}${CIRCULANT_GRAPH_URL}/${id}`, { signal: signal })
        .then((response) => {
            if (response.status !== 200) {
                throw new Error(response.status + response.statusText);
            }
            return response.data;
        });

export const postCirculantGraph = (params: {
    order: number;
}): Promise<CirculantGraph> =>
    axios
        .post(`${API_URL}${CIRCULANT_GRAPH_URL}`, params)
        .then((response) => response.data);

export const optionsCirculantGraph = (): Promise<CirculantGraphOptions> =>
    axios
        .options(`${API_URL}${CIRCULANT_GRAPH_URL}`)
        .then(
            (response) => formatOptions(response.data) as CirculantGraphOptions
        );
