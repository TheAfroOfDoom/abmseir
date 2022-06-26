import axios, { AxiosRequestConfig } from 'axios';

import { API_URL } from '../..';
import { formatOptions, PaginatedResponse } from '../common';
import { GraphOptions, Graph } from './common';

const COMPLETE_GRAPH_URL = '/graphs/complete';

interface CompleteGraph extends Graph {}

interface CompleteGraphResults extends Omit<PaginatedResponse, 'results'> {
    results: CompleteGraph[];
}

export interface CompleteGraphOptions extends GraphOptions {}

// TODO: Merge these into a single call that will fetch graph data if id param is specified
export const getCompleteGraphs = (): Promise<CompleteGraphResults> =>
    axios
        .get(`${API_URL}${COMPLETE_GRAPH_URL}`)
        .then((response) => response.data);

export const getCompleteGraph = (
    id: string,
    signal?: AxiosRequestConfig['signal']
): Promise<CompleteGraph & { data: Blob }> =>
    axios
        .get(`${API_URL}${COMPLETE_GRAPH_URL}/${id}`, { signal: signal })
        .then((response) => {
            if (response.status !== 200) {
                throw new Error(response.status + response.statusText);
            }
            return response.data;
        });

export const postCompleteGraph = (params: {
    order: number;
}): Promise<CompleteGraph> =>
    axios
        .post(`${API_URL}${COMPLETE_GRAPH_URL}`, params)
        .then((response) => response.data);

export const optionsCompleteGraph = (): Promise<CompleteGraphOptions> =>
    axios
        .options(`${API_URL}${COMPLETE_GRAPH_URL}`)
        .then(
            (response) => formatOptions(response.data) as CompleteGraphOptions
        );
