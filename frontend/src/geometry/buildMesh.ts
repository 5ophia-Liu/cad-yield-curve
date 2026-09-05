import * as THREE from 'three';

const yScale = 3;
const zLength = 30;

function buildSurfaceGeometry(maturities: number[], curves: number[][], dates: string[]): THREE.BufferGeometry {
    // x = maturities [j]
    // y = curves[i][j] (the yield value)
    // z = dates [i]

    const rows = dates.length; // index i
    const cols = maturities.length; // index j
    const positions = new Float32Array(rows*cols*3);
    const zScale = zLength/dates.length

    //flatten
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const ind = (row * cols + col) * 3;
            positions[ind] = maturities[col]; // x
            positions[ind+1] = curves[row][col]*yScale; // y
            positions[ind+2] = row*zScale; // z
        }
    }

    const indices: number[] = [];
    for (let row = 0; row < rows - 1; row++) {
        for (let col = 0; col < cols - 1; col++) {
            const a = row * cols + col;         // (row, col)
            const b = row * cols + (col + 1);   // (row, col+1)
            const c = (row + 1) * cols + col;   // (row+1, col)
            const d = (row + 1) * cols + (col + 1); // (row+1, col+1)

            indices.push(a, c, b); // triangle 1
            indices.push(b, c, d); // triangle 2
        }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    
    return geometry;
}

function getMaxScaledYield(curves: number[][]): number {
    return Math.max(...curves.flat()) * yScale;
}

export { buildSurfaceGeometry, zLength, getMaxScaledYield };