import { useState, useEffect, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text, Grid } from "@react-three/drei";
import * as THREE from 'three';
import './App.css'
import { fetchCurveData } from "./services/curve-api";
import { buildSurfaceGeometry, zLength, getMaxScaledYield, yScale } from './geometry/buildMesh';

const start_date = '2020-01-01';
const end_date = '2025-12-31';

// generate curve surface
function YieldSurface({ dates, maturities, curves }: { dates: string[]; maturities: number[]; curves: number[][] }) {
  const geometry = useMemo(
    () => buildSurfaceGeometry(maturities, curves, dates),
    [maturities, curves, dates]
  );

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial vertexColors side={THREE.DoubleSide} />
    </mesh>
  );
}

// generate grid underneath
function BaselinePlane({ width, depth }: { width: number; depth: number }) {
  return (
    <Grid
      position={[width / 2, 0, depth / 2]}
      args={[width, depth]}
      cellSize={1}
      cellThickness={0.6}
      cellColor="#2a3040"
      sectionSize={4}
      sectionThickness={1.2}
      sectionColor="#a0a4ad"
      fadeDistance={80}
      fadeStrength={0.5}
      infiniteGrid={false}
      followCamera={false}
    />
  );
}

//label axes
function AxisLabels({maxMaturity, minMaturity, maxScaledYield, zLength} : { maxMaturity: number; minMaturity: number; maxScaledYield: number; zLength: number }) {
  return (
    <>
      <Text position={[maxMaturity + 7, 0.75, 0]} fontSize={1.5} color="#e8e8e8">
        Maturity
      </Text>
      <Text
        position={[minMaturity, 0.75, zLength + 7]}
        fontSize={1.5}
        color="#e8e8e8"
        rotation={[0, Math.PI / 2, 0]}
      >
        Date
      </Text>
      <Text position={[minMaturity, maxScaledYield + 5, 0]} fontSize={1.5} color="#e8e8e8">
        Yield
      </Text>
    </>
  );
}

// generate indices
function pickEvenIndices(length: number, count: number): number[] {
  if (length <= count) return Array.from({ length }, (_, i) => i);
  const step = (length - 1) / (count - 1);
  return Array.from({ length: count }, (_, i) => Math.round(i * step));
}

function formatDateShort(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
}

function AxisTicks({ dates, maturities, maxScaledYield, zLength, yScale}: { dates: string[]; maturities: number[]; maxScaledYield: number; zLength: number; yScale: number }) {
  const zScale = zLength / dates.length;

  const maturityTickIdx = pickEvenIndices(maturities.length, 6);
  const dateTickIdx = pickEvenIndices(dates.length, 6);
  const yieldStep = Math.max(1, Math.ceil(maxScaledYield / 5));
  const yieldTicks: number[] = [];
  for (let y = 0; y <= Math.ceil(maxScaledYield); y += yieldStep) yieldTicks.push(y);

  return (
    <>
      {maturityTickIdx.map((i) => (
        <Text
          key={`mat-${i}`}
          position={[maturities[i], 0.5, 0]}
          fontSize={0.9}
          color="#9aa0ac"
        >
          {maturities[i]}Y
        </Text>
      ))}

      {dateTickIdx.map((i) => (
        <Text
          key={`date-${i}`}
          position={[0, 0.5, i * zScale]}
          fontSize={0.9}
          color="#9aa0ac"
          rotation={[0, Math.PI / 2, 0]}
        >
          {formatDateShort(dates[i])}
        </Text>
      ))}

      {yieldTicks.map((y) => (
        <Text
          key={`yield-${y}`}
          position={[0, y, 0]}
          fontSize={0.9}
          color="#9aa0ac"
        >
          {Math.ceil(y / yScale)}%
        </Text>
      ))}
    </>
  );
}

function App() {
  const [data, setData] = useState<{
    dates: string[];
    maturities: number[];
    curves: number[][];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchCurveData(start_date, end_date);
        setData(data);
      } catch (e) {
        setError((e as Error).message);
      }
    }

    load();
  }, []);
  if(error) {return <div>Error: {error}</div>;}
  if(!data) {return <div>Loading...</div>}

  const maxMaturity = Math.max(...data.maturities);
  const minMaturity = Math.min(...data.maturities);
  const maxScaledYield = getMaxScaledYield(data.curves);

  return(
    <>
    <div style={{ width: "100vw", height: "100vh", background: "#0a0d14" }}>
      <Canvas camera={{ position: [40, 30, 60], fov: 50 }}>
        <color attach="background" args={["#0a0d14"]} />
        <ambientLight intensity={0.8} />
        <directionalLight position={[50, 80, 50]} intensity={1.2} />
        <YieldSurface
          dates={data.dates}
          maturities={data.maturities}
          curves={data.curves}
        />
        <BaselinePlane width={maxMaturity - minMaturity} depth={zLength} />
        <AxisLabels maxMaturity={maxMaturity} minMaturity={minMaturity} maxScaledYield={maxScaledYield} zLength={zLength} />
        <AxisTicks
          dates={data.dates}
          maturities={data.maturities}
          maxScaledYield={maxScaledYield}
          zLength={zLength}
          yScale={yScale}
        />
        <primitive object={new THREE.AxesHelper(40)} />
        <OrbitControls />
      </Canvas>
    </div>
  </>)
}

export default App