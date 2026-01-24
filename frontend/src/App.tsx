import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';

import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Channels from './pages/Channels';
import ChannelDetail from './pages/ChannelDetail';
import Queue from './pages/Queue';
import Calendar from './pages/Calendar';
import Statistics from './pages/Statistics';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

function App() {
  return (
    <Layout>
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/channels" element={<Channels />} />
          <Route path="/channels/:id" element={<ChannelDetail />} />
          <Route path="/queue" element={<Queue />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Box>
    </Layout>
  );
}

export default App;
