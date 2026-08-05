import React from 'react';
import { GuestLayout } from '../layouts/GuestLayout';
import { HomePage } from '../pages/public/HomePage';

export const App: React.FC = () => {
  return (
    <GuestLayout>
      <HomePage />
    </GuestLayout>
  );
};
export default App;
