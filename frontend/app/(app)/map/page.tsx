'use client'

import { useState } from 'react'
import {
  Map as MapIcon, Layers, Navigation, AlertCircle,
  CheckCircle2, Compass, Eye, Filter
} from 'lucide-react'

interface ZonePin {
  id: string
  name: string
  lat: number
  lng: number
  discipline: string
  progress: number
  status: 'active' | 'delayed' | 'completed'
  supervisor: string
  last_activity: string
}

const SITE_PINS: ZonePin[] = [
  {
    id: 'z1',
    name: 'Trench Section CH 0+000 - CH 0+450',
    lat: 26.578,
    lng: 93.172,
    discipline: 'Civil',
    progress: 100,
    status: 'completed',
    supervisor: 'Mahanta',
    last_activity: 'Excavation completed and certified',
  },
  {
    id: 'z2',
    name: 'Field Joint Welding CH 0+000 - CH 0+300',
    lat: 26.582,
    lng: 93.176,
    discipline: 'Piping',
    progress: 72,
    status: 'active',
    supervisor: 'Rajesh Kumar (AWS)',
    last_activity: '18 of 25 field joints welded',
  },
  {
    id: 'z3',
    name: 'Pump Station Inlet Manifold Header',
    lat: 26.585,
    lng: 93.181,
    discipline: 'Piping',
    progress: 40,
    status: 'delayed',
    supervisor: 'D. Kalita',
    last_activity: 'Spool PS-IN-003 fit-up done, crane rigged',
  },
  {
    id: 'z4',
    name: 'MCC-01 to FJB-03 Cable Corridor',
    lat: 26.579,
    lng: 93.185,
    discipline: 'Electrical',
    progress: 25,
    status: 'active',
    supervisor: 'Priya Nath',
    last_activity: 'Cable tray erected, pulling underway',
  },
]

export default function MapPage() {
  const [selectedPin, setSelectedPin] = useState<ZonePin>(SITE_PINS[1])
  const [activeDiscipline, setActiveDiscipline] = useState<string>('all')

  const filteredPins = SITE_PINS.filter((p) => {
    if (activeDiscipline === 'all') return true
    return p.discipline.toLowerCase() === activeDiscipline.toLowerCase()
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface border border-border rounded-xl p-5">
        <div>
          <div className="flex items-center gap-2">
            <MapIcon className="w-5 h-5 text-primary" />
            <h1 className="text-xl font-bold text-white">Geospatial Telemetry & Discipline Heatmap</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-mono border border-blue-500/20">
              KAZIRANGA PIPELINE CORRIDOR
            </span>
          </div>
          <p className="text-sm text-text-muted mt-1">
            GIS spatial mapping of physical L5/L6 execution coordinates with geofenced supervisor submission validation
          </p>
        </div>

        {/* Discipline Filter */}
        <div className="flex bg-surface-card p-1 rounded-lg border border-border">
          {['all', 'Piping', 'Civil', 'Electrical'].map((d) => (
            <button
              key={d}
              onClick={() => setActiveDiscipline(d)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                activeDiscipline === d ? 'bg-surface border border-border text-white' : 'text-text-muted hover:text-white'
              }`}
            >
              {d === 'all' ? 'All Zones' : d}
            </button>
          ))}
        </div>
      </div>

      {/* Map Interactive Visualizer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Spatial Map Canvas */}
        <div className="lg:col-span-8 bg-surface border border-border rounded-xl p-6 relative overflow-hidden min-h-[460px] flex flex-col justify-between">
          {/* Simulated Satellite/Topographic Canvas */}
          <div className="absolute inset-0 bg-[#070b14] opacity-90">
            {/* Grid Lines for GIS feeling */}
            <div className="w-full h-full bg-[linear-gradient(to_right,#1f293715_1px,transparent_1px),linear-gradient(to_bottom,#1f293715_1px,transparent_1px)] bg-[size:32px_32px]" />
          </div>

          {/* Top Spatial Overlay */}
          <div className="relative z-10 flex items-center justify-between">
            <div className="bg-surface-card/80 backdrop-blur border border-border px-3 py-1.5 rounded-lg text-[11px] font-mono text-text-muted flex items-center gap-2">
              <Compass className="w-3.5 h-3.5 text-primary" />
              <span>COORDS: 26.582° N, 93.176° E</span>
            </div>
            <div className="bg-surface-card/80 backdrop-blur border border-border px-3 py-1.5 rounded-lg text-[11px] font-mono text-emerald-400">
              GEOFENCE: VERIFIED (4 ACTIVE ZONES)
            </div>
          </div>

          {/* Interactive Pins on Canvas */}
          <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-4 my-auto">
            {filteredPins.map((pin) => {
              const isSelected = selectedPin.id === pin.id
              return (
                <div
                  key={pin.id}
                  onClick={() => setSelectedPin(pin)}
                  className={`p-4 rounded-xl border cursor-pointer backdrop-blur transition-all ${
                    isSelected
                      ? 'bg-primary/20 border-primary ring-2 ring-primary/40 shadow-lg'
                      : 'bg-surface-card/90 border-border hover:border-border-active'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-[10px] font-mono text-text-muted">{pin.discipline}</span>
                  </div>
                  <h4 className="text-xs font-semibold text-white truncate">{pin.name}</h4>
                  <div className="mt-3 flex items-center justify-between text-[11px]">
                    <span className="text-text-muted">Progress</span>
                    <span className="font-mono font-bold text-white">{pin.progress}%</span>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Bottom Satellite Info */}
          <div className="relative z-10 flex items-center justify-between text-xs text-text-muted pt-4 border-t border-border/40">
            <span>Spatial Layer: <strong className="text-white">Pipeline ROW Alignment Corridor</strong></span>
            <span>Terrain: Brahmaputra River Basin Floodplain</span>
          </div>
        </div>

        {/* Selected Zone Telemetry Card */}
        <div className="lg:col-span-4 bg-surface border border-border rounded-xl p-5 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="pb-3 border-b border-border">
              <span className="text-[10px] font-mono text-primary uppercase">Zone Telemetry Detail</span>
              <h3 className="text-sm font-semibold text-white mt-1">{selectedPin.name}</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between p-3 rounded-lg bg-surface-card border border-border">
                <span className="text-text-muted">Discipline</span>
                <strong className="text-blue-400 font-mono">{selectedPin.discipline}</strong>
              </div>

              <div className="flex justify-between p-3 rounded-lg bg-surface-card border border-border">
                <span className="text-text-muted">Field Supervisor</span>
                <strong className="text-white">{selectedPin.supervisor}</strong>
              </div>

              <div className="flex justify-between p-3 rounded-lg bg-surface-card border border-border">
                <span className="text-text-muted">Execution Velocity</span>
                <strong className="text-emerald-400 font-mono">{selectedPin.progress}% Completed</strong>
              </div>

              <div className="p-3 rounded-lg bg-surface-card border border-border space-y-1">
                <span className="text-[11px] text-text-muted block">Latest Field Log Update</span>
                <p className="text-xs text-white font-medium italic">
                  &quot;{selectedPin.last_activity}&quot;
                </p>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-border mt-4">
            <button
              type="button"
              className="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg transition-colors"
            >
              Filter WBS Activities for Zone
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
