import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Grid,
  FormControlLabel,
  Switch,
} from '@mui/material';
import { Clear } from '@mui/icons-material';
import { ScheduleFilters } from '../../services/schedules';

interface CalendarFiltersProps {
  filters: ScheduleFilters;
  channels: Array<{ id: string; name: string }>;
  onChange: (filters: ScheduleFilters) => void;
  onClear: () => void;
}

export default function CalendarFilters({
  filters,
  channels,
  onChange,
  onClear,
}: CalendarFiltersProps) {
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
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status || ''}
              label="Status"
              onChange={(e) =>
                onChange({ ...filters, status: e.target.value || undefined })
              }
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="scheduled">Scheduled</MenuItem>
              <MenuItem value="executing">Executing</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Type</InputLabel>
            <Select
              value={filters.scheduleType || ''}
              label="Type"
              onChange={(e) =>
                onChange({ ...filters, scheduleType: e.target.value || undefined })
              }
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="simultaneous">Simultaneous</MenuItem>
              <MenuItem value="staggered">Staggered</MenuItem>
              <MenuItem value="independent">Independent</MenuItem>
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

        <Grid item xs={12} sm={6} md={1}>
          <FormControlLabel
            control={
              <Switch
                checked={filters.includeHistory || false}
                onChange={(e) =>
                  onChange({ ...filters, includeHistory: e.target.checked })
                }
              />
            }
            label="History"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={1}>
          <Button
            variant="outlined"
            startIcon={<Clear />}
            onClick={onClear}
            size="small"
            fullWidth
          >
            Clear
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}
