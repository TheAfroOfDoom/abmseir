import React, { useRef } from 'react';
import cytoscape, { use as cytoscapeUse } from 'cytoscape';
import avsdf from 'cytoscape-avsdf';
import CytoscapeComponent from 'react-cytoscapejs';

cytoscapeUse(avsdf);

const cyCss = {
    width: '100%',
    height: '100%',
};

export const CytoscapeStyled: React.FC<CytoscapeComponent['props']> = (
    props
): JSX.Element => {
    let { elements, layout } = props;
    const cyRef = useRef<cytoscape.Core>();

    elements = elements.map((element) => {
        if (element.data.label === undefined) {
            return { ...element, data: { ...element.data, label: '' } };
        }
        return element;
    });
    // TODO: Choose good default layout here
    // https://blog.js.cytoscape.org/2020/05/11/layouts/#choice-of-layout
    layout = layout || { name: 'avsdf' };

    return (
        <CytoscapeComponent
            {...props}
            cy={(cy): void => {
                cyRef.current = cy;
            }}
            elements={elements}
            layout={layout}
            style={cyCss}
        />
    );
};
export default CytoscapeStyled;
