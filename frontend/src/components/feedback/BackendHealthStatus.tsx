import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  Activity, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Server, 
  Database, 
  Clock, 
  Code2 
} from 'lucide-react';
import { API_CONFIG } from '../../constants/api.constants';

interface HealthResponse {
  status: string;
}

export const BackendHealthStatus: React.FC = () => {
  const [healthState, setHealthState] = useState<'idle' | 'loading' | 'healthy' | 'error'>('idle');
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [latency, setLatency] = useState<number | null>(null);
  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    setHealthState('loading');
    setErrorMessage(null);
    const startTime = performance.now();

    try {
      // Health check endpoint URL
      const targetUrl = `${API_CONFIG.BASE_URL.replace(/\/v1\/?$/, '')}/health/`;
      const response = await axios.get<HealthResponse>(targetUrl, {
        timeout: 5000,
        headers: { 'Accept': 'application/json' },
      });

      const endTime = performance.now();
      const durationMs = Math.round(endTime - startTime);

      setLatency(durationMs);
      setHealthData(response.data);
      setLastChecked(new Date().toLocaleTimeString());

      if (response.data && response.data.status === 'healthy') {
        setHealthState('healthy');
      } else {
        setHealthState('error');
        setErrorMessage(`Unexpected status: ${JSON.stringify(response.data)}`);
      }
    } catch (err: unknown) {
      const endTime = performance.now();
      setLatency(Math.round(endTime - startTime));
      setHealthState('error');
      setLastChecked(new Date().toLocaleTimeString());

      if (axios.isAxiosError(err)) {
        setErrorMessage(err.message || 'Failed to connect to backend server.');
      } else {
        setErrorMessage('An unexpected network error occurred.');
      }
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 space-y-6 border border-slate-800/80 shadow-2xl relative overflow-hidden">
      {/* Background Subtle Gradient */}
      <div className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-500/10 blur-3xl" />

      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800/80 pb-5 gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="p-3 rounded-xl bg-brand-500/10 border border-brand-500/20 text-brand-400">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white font-heading">
              Full Stack System Connection
            </h3>
            <p className="text-xs text-slate-400">
              React 19 Frontend ↔ Django 5 Backend ↔ PostgreSQL 16 DB
            </p>
          </div>
        </div>

        {/* Status Pill Badge */}
        <div className="flex items-center space-x-3">
          {healthState === 'loading' && (
            <div className="inline-flex items-center space-x-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-3.5 py-1.5 text-xs font-semibold text-amber-400 backdrop-blur-md">
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
              <span>Connecting...</span>
            </div>
          )}

          {healthState === 'healthy' && (
            <div className="inline-flex items-center space-x-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-1.5 text-xs font-semibold text-emerald-400 backdrop-blur-md shadow-lg shadow-emerald-500/10">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="font-mono tracking-wide">CONNECTIVITY_HEALTHY</span>
            </div>
          )}

          {healthState === 'error' && (
            <div className="inline-flex items-center space-x-2 rounded-full border border-rose-500/30 bg-rose-500/10 px-3.5 py-1.5 text-xs font-semibold text-rose-400 backdrop-blur-md shadow-lg shadow-rose-500/10">
              <XCircle className="h-4 w-4 text-rose-400" />
              <span className="font-mono tracking-wide">CONNECTION_FAILED</span>
            </div>
          )}

          <button
            onClick={checkHealth}
            disabled={healthState === 'loading'}
            className="inline-flex items-center space-x-1.5 rounded-xl border border-slate-700 bg-slate-800/60 hover:bg-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white transition-all disabled:opacity-50"
            title="Re-check Health Status"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${healthState === 'loading' ? 'animate-spin' : ''}`} />
            <span>Re-check</span>
          </button>
        </div>
      </div>

      {/* Metrics & Details Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Backend Endpoint Status */}
        <div className="glass-card rounded-xl p-4 space-y-2 border border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Backend Status</span>
            <Server className="h-4 w-4 text-brand-400" />
          </div>
          <p className="text-sm font-semibold text-white font-mono">
            {healthState === 'healthy' ? '200 OK' : healthState === 'error' ? 'Error' : 'Pending'}
          </p>
          <p className="text-[11px] text-slate-500 truncate">
            GET /api/health/
          </p>
        </div>

        {/* PostgreSQL Database */}
        <div className="glass-card rounded-xl p-4 space-y-2 border border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>PostgreSQL Database</span>
            <Database className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="text-sm font-semibold text-white font-mono">
            {healthState === 'healthy' ? 'Connected' : 'Unavailable'}
          </p>
          <p className="text-[11px] text-slate-500">prepora_db @ postgres:5432</p>
        </div>

        {/* Latency */}
        <div className="glass-card rounded-xl p-4 space-y-2 border border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Round-Trip Latency</span>
            <Clock className="h-4 w-4 text-amber-400" />
          </div>
          <p className="text-sm font-semibold text-white font-mono">
            {latency !== null ? `${latency} ms` : '--'}
          </p>
          <p className="text-[11px] text-slate-500">
            {lastChecked ? `Checked at ${lastChecked}` : 'Not checked'}
          </p>
        </div>

        {/* API Response JSON */}
        <div className="glass-card rounded-xl p-4 space-y-2 border border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>API Response</span>
            <Code2 className="h-4 w-4 text-indigo-400" />
          </div>
          <p className="text-sm font-semibold text-emerald-400 font-mono truncate">
            {healthData ? JSON.stringify(healthData) : errorMessage ? 'Error' : '{}'}
          </p>
          <p className="text-[11px] text-slate-500">JSON Payload</p>
        </div>
      </div>

      {/* Error Banner if error occurred */}
      {errorMessage && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300 flex items-start space-x-2">
          <XCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Connection Failure: </span>
            <span>{errorMessage}</span>
          </div>
        </div>
      )}
    </div>
  );
};
