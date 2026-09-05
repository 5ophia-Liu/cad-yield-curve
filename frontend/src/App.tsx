import { useState, useEffect, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from "@react-three/drei";
import * as THREE from 'three';
import './App.css'
import { fetchCurveData } from "./services/curve-api";
import { buildSurfaceGeometry, zLength, getMaxScaledYield } from './geometry/buildMesh';

// test variables
const start_date = '2020-01-01';
const end_date = '2025-12-01';

function YieldSurface({ dates, maturities, curves }: { dates: string[]; maturities: number[]; curves: number[][] }) {
  const geometry = useMemo(
    () => buildSurfaceGeometry(maturities, curves, dates),
    [maturities, curves, dates]
  );

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial color="lightblue" side={THREE.DoubleSide} />
    </mesh>
  );
}

function BaselinePlane({ width, depth }: { width: number; depth: number }) {
  return (
    <mesh
      position={[width / 2, 0, depth / 2]}
      rotation={[-Math.PI / 2, 0, 0]}
    >
      <planeGeometry args={[width, depth]} />
      <meshStandardMaterial color="lightgray" side={THREE.DoubleSide} />
    </mesh>
  );
}

function AxisLabels({maxMaturity, minMaturity, maxYield, zLength} : { maxMaturity: number; minMaturity: number; maxYield: number; zLength: number }) {
  return (
    <>
      <Text position={[maxMaturity + 10, 0, 0]} fontSize={1.5} color="black">
        Maturity (years)
      </Text>
      <Text
        position={[minMaturity, 0, zLength + 7]}
        fontSize={1.5}
        color="black"
        rotation={[0, Math.PI / 2, 0]}
      >
        Time
      </Text>
      <Text position={[minMaturity - 2, maxYield + 2, 0]} fontSize={1.5} color="black">
        Yield (%)
      </Text>
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
  const maxYield = getMaxScaledYield(data.curves);

  return(
    <>
    <div style={{ width: "100vw", height: "100vh" }}>
      <Canvas camera={{ position: [40, 30, 60], fov: 50 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[50, 80, 50]} intensity={1} />
        <YieldSurface
          dates={data.dates}
          maturities={data.maturities}
          curves={data.curves}
        />
        <BaselinePlane width={maxMaturity - minMaturity} depth={zLength} />
        <AxisLabels maxMaturity={maxMaturity} minMaturity={minMaturity} maxYield={maxYield} zLength={zLength} />
        <primitive object={new THREE.AxesHelper(40)} />
        <OrbitControls />
      </Canvas>
    </div>
  </>)
}

export default App
