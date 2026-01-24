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
import { Clear, Download } from '@mui/icons-material';
import { StatisticsFilters as StatsFilters } from '../../services/statistics';

interface StatisticsFiltersProps {
  filters: StatsFilters;
  channels: Array<{ id: string; name: string }>;
  onChange: (filters: StatsFilters) => void;
  onClear: () => void;
  onExport?: (format: 'csv' | 'json') => void;
}

export default function StatisticsFilters({
  filters,
  channels,
  onChange,
  onClear,
  onExport,
}: StatisticsFiltersProps) {
  return (
    <Box sx={{ mb: 2 }}>
      <Grid container spacing={2} alignItems="center">
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
            <InputLabel>Metric</InputLabel>
            <Select
              value={filters.metric || ''}
              label="Metric"
              onChange={(e) =>
                onChange({ ...filters, metric: e.target.value || undefined })
              }
            >
              <MenuItem value="">All Metrics</MenuItem>
              <MenuItem value="subscribers">Subscribers</MenuItem>
              <MenuItem value="views">Views</MenuItem>
              <MenuItem value="videos">Videos</MenuItem>
              <MenuItem value="engagement">Engagement</MenuItem>
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
          <TextField
            fullWidth
            size="small"
            type="date"
            label="End Date"
            value={filters.endDate || ''}
            onChange={(e) =>
              onChange({ ...filters, endDate: e.target.value || undefined })
            }
            InputLabelProps={{ shrink: true }}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Box display="flex" gap={1}>
            <Button
              variant="outlined"
              startIcon={<Clear />}
              onClick={onClear}
              size="small"
            >
              Clear
            </Button>
            {onExport && (
              <>
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  onClick={() => onExport('csv')}
                  size="small"
                >
                  CSV
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  onClick={() => onExport('json')}
                  size="small"
                >
                  JSON
                </Button>
              </>
            )}
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
