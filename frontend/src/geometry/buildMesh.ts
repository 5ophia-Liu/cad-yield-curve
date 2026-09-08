import * as THREE from 'three';

const yScale = 3;
const zLength = 30;

// (low) blue -> cyan -> green -> yellow -> red (high)
function yieldToColor(t: number): [number, number, number] {
    const stops: [number, number, number][] = [
        [0.10, 0.10, 0.60],
        [0.10, 0.55, 0.85],
        [0.20, 0.75, 0.45],
        [0.95, 0.85, 0.25],
        [0.85, 0.20, 0.15],
    ];
    const n = stops.length - 1;
    const scaled = Math.min(Math.max(t, 0), 1) * n;
    const idx = Math.min(Math.floor(scaled), n - 1);
    const frac = scaled - idx;
    const [r0, g0, b0] = stops[idx];
    const [r1, g1, b1] = stops[idx + 1];
    return [
        r0 + (r1 - r0) * frac,
        g0 + (g1 - g0) * frac,
        b0 + (b1 - b0) * frac,
    ];
}

function buildSurfaceGeometry(maturities: number[], curves: number[][], dates: string[]): THREE.BufferGeometry {
    const rows = dates.length;
    const cols = maturities.length;
    const positions = new Float32Array(rows * cols * 3);
    const colors = new Float32Array(rows * cols * 3);
    const zScale = zLength / dates.length;

    const flatYields = curves.flat();
    const minYield = Math.min(...flatYields);
    const maxYield = Math.max(...flatYields);
    const range = maxYield - minYield || 1; // avoid divide-by-zero on flat data

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const ind = (row * cols + col) * 3;
            const yieldValue = curves[row][col];

            positions[ind] = maturities[col];
            positions[ind + 1] = yieldValue * yScale;
            positions[ind + 2] = row * zScale;

            const t = (yieldValue - minYield) / range;
            const [r, g, b] = yieldToColor(t);
            colors[ind] = r;
            colors[ind + 1] = g;
            colors[ind + 2] = b;
        }
    }

    const indices: number[] = [];
    for (let row = 0; row < rows - 1; row++) {
        for (let col = 0; col < cols - 1; col++) {
            const a = row * cols + col;
            const b = row * cols + (col + 1);
            const c = (row + 1) * cols + col;
            const d = (row + 1) * cols + (col + 1);

            indices.push(a, c, b);
            indices.push(b, c, d);
        }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();

    return geometry;
}

function getMaxScaledYield(curves: number[][]): number {
    return Math.max(...curves.flat()) * yScale;
}

export { buildSurfaceGeometry, zLength, getMaxScaledYield, yScale };