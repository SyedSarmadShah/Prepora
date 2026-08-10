import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { GuestLayout } from '../layouts/GuestLayout';
import { HomePage } from '../pages/public/HomePage';
import { ProtectedRoute } from './ProtectedRoute';
import { RoleGuard } from './RoleGuard';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/"
        element={
          <GuestLayout>
            <HomePage />
          </GuestLayout>
        }
      />
      <Route
        path="/login"
        element={
          <GuestLayout>
            <div className="container mx-auto px-4 py-20 text-center">
              <h1 className="text-3xl font-bold text-slate-100 mb-4">Login Page</h1>
              <p className="text-slate-400">Authentication pages will be implemented in the next step.</p>
            </div>
          </GuestLayout>
        }
      />
      <Route
        path="/unauthorized"
        element={
          <GuestLayout>
            <div className="container mx-auto px-4 py-20 text-center">
              <h1 className="text-3xl font-bold text-rose-500 mb-4">403 - Unauthorized Access</h1>
              <p className="text-slate-400">You do not have permission to access this resource.</p>
            </div>
          </GuestLayout>
        }
      />

      {/* Protected Routes (Authenticated Users Only) */}
      <Route element={<ProtectedRoute />}>
        <Route
          path="/dashboard"
          element={
            <GuestLayout>
              <div className="container mx-auto px-4 py-20 text-center">
                <h1 className="text-3xl font-bold text-emerald-400 mb-4">Student Dashboard</h1>
                <p className="text-slate-400">Protected area accessible to authenticated users.</p>
              </div>
            </GuestLayout>
          }
        />
      </Route>

      {/* Role Guarded Routes (ADMIN & SUPERADMIN Only) */}
      <Route element={<RoleGuard allowedRoles={['ADMIN', 'SUPERADMIN']} />}>
        <Route
          path="/admin"
          element={
            <GuestLayout>
              <div className="container mx-auto px-4 py-20 text-center">
                <h1 className="text-3xl font-bold text-brand-400 mb-4">Admin Panel</h1>
                <p className="text-slate-400">Role-restricted area accessible to ADMIN and SUPERADMIN roles.</p>
              </div>
            </GuestLayout>
          }
        />
      </Route>

      {/* Fallback Catch-All Route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
