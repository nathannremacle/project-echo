import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Grid,
} from '@mui/material';
import { Clear } from '@mui/icons-material';
import { QueueFilters } from '../../services/queue';

interface QueueFiltersProps {
  filters: QueueFilters;
  channels: Array<{ id: string; name: string }>;
  onChange: (filters: QueueFilters) => void;
  onClear: () => void;
}

export default function QueueFiltersComponent({
  filters,
  channels,
  onChange,
  onClear,
}: QueueFiltersProps) {
  return (
    <Box sx={{ mb: 2 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status || ''}
              label="Status"
              onChange={(e) =>
                onChange({ ...filters, status: e.target.value || undefined })
              }
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="queued">Queued</MenuItem>
              <MenuItem value="processing">Processing</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
              <MenuItem value="retrying">Retrying</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Channel</InputLabel>
            <Select
              value={filters.channelId || ''}
              label="Channel"
              onChange={(e) =>
                onChange({ ...filters, channelId: e.target.value || undefined })
              }
            >
              <MenuItem value="">All Channels</MenuItem>
              {channels.map((channel) => (
                <MenuItem key={channel.id} value={channel.id}>
                  {channel.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Job Type</InputLabel>
            <Select
              value={filters.jobType || ''}
              label="Job Type"
              onChange={(e) =>
                onChange({ ...filters, jobType: e.target.value || undefined })
              }
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="scrape">Scrape</MenuItem>
              <MenuItem value="download">Download</MenuItem>
              <MenuItem value="transform">Transform</MenuItem>
              <MenuItem value="publish">Publish</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <TextField
            fullWidth
            size="small"
            type="date"
            label="Start Date"
            value={filters.startDate || ''}
            onChange={(e) =>
              onChange({ ...filters, startDate: e.target.value || undefined })
            }
            InputLabelProps={{ shrink: true }}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Box display="flex" gap={1}>
            <Button
              variant="outlined"
              startIcon={<Clear />}
              onClick={onClear}
              size="small"
            >
              Clear
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
