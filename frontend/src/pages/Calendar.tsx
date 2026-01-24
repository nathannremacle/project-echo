import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { scheduleService, ScheduleFilters } from '../services/schedules';
import CalendarView from '../components/calendar/CalendarView';
import CalendarFilters from '../components/calendar/CalendarFilters';
import ConflictIndicator from '../components/calendar/ConflictIndicator';
import { PublicationSchedule } from '../services/schedules';
import { orchestrationService } from '../services/orchestration';

export default function Calendar() {
  const queryClient = useQueryClient();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'day' | 'week' | 'month'>('week');
  const [filters, setFilters] = useState<ScheduleFilters>({});
  const [selectedSchedule, setSelectedSchedule] = useState<PublicationSchedule | null>(null);
  const [rescheduleDialogOpen, setRescheduleDialogOpen] = useState(false);
  const [newScheduleDate, setNewScheduleDate] = useState('');

  // Fetch schedules
  const {
    data: schedules,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['schedules', filters, currentDate],
    queryFn: () => scheduleService.getSchedules(filters),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Fetch channels for filter
  const { data: channelsData } = useQuery({
    queryKey: ['channels-list'],
    queryFn: async () => {
      const dashboard = await orchestrationService.getDashboard();
      return {
        channels: dashboard.channels.statuses.map((s) => ({
          id: s.channel_id,
          name: s.name,
        })),
      };
    },
  });

  // Update schedule mutation
  const updateMutation = useMutation({
    mutationFn: ({ scheduleId, updates }: { scheduleId: string; updates: any }) =>
      scheduleService.updateSchedule(scheduleId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
      setRescheduleDialogOpen(false);
      setSelectedSchedule(null);
    },
  });

  // Cancel schedule mutation
  const cancelMutation = useMutation({
    mutationFn: (scheduleId: string) => scheduleService.cancelSchedule(scheduleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
    },
  });

  const handleScheduleClick = (schedule: PublicationSchedule) => {
    setSelectedSchedule(schedule);
  };

  const handleReschedule = (scheduleId: string, newDate: Date) => {
    setSelectedSchedule(schedules?.find((s) => s.id === scheduleId) || null);
    setNewScheduleDate(newDate.toISOString().slice(0, 16));
    setRescheduleDialogOpen(true);
  };

  const handleSaveReschedule = () => {
    if (selectedSchedule) {
      updateMutation.mutate({
        scheduleId: selectedSchedule.id,
        updates: {
          scheduledAt: new Date(newScheduleDate).toISOString(),
        },
      });
    }
  };

  const handleCancelSchedule = (scheduleId: string) => {
    if (window.confirm('Are you sure you want to cancel this schedule?')) {
      cancelMutation.mutate(scheduleId);
    }
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load calendar: {error instanceof Error ? error.message : 'Unknown error'}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Publication Calendar</Typography>
        <Tooltip title="Refresh">
          <IconButton
            onClick={() => {
              queryClient.invalidateQueries({ queryKey: ['schedules'] });
            }}
          >
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Conflict Indicator */}
      {schedules && schedules.length > 0 && (
        <ConflictIndicator schedules={schedules} />
      )}

      {/* Filters */}
      <CalendarFilters
        filters={filters}
        channels={channelsData?.channels || []}
        onChange={setFilters}
        onClear={handleClearFilters}
      />

      {/* Calendar View */}
      {schedules && (
        <CalendarView
          schedules={schedules}
          currentDate={currentDate}
          view={view}
          onDateChange={setCurrentDate}
          onViewChange={setView}
          onScheduleClick={handleScheduleClick}
          onScheduleReschedule={handleReschedule}
        />
      )}

      {/* Schedule Detail Dialog */}
      <Dialog
        open={!!selectedSchedule && !rescheduleDialogOpen}
        onClose={() => setSelectedSchedule(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Schedule Details</DialogTitle>
        <DialogContent>
          {selectedSchedule && (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Scheduled At: {new Date(selectedSchedule.scheduledAt).toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Status: {selectedSchedule.status}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Type: {selectedSchedule.scheduleType}
              </Typography>
              {selectedSchedule.videoId && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Video: {selectedSchedule.videoId}
                </Typography>
              )}
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Channel: {selectedSchedule.channelId}
              </Typography>
              {selectedSchedule.waveId && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Wave ID: {selectedSchedule.waveId}
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedSchedule(null)}>Close</Button>
          {selectedSchedule && selectedSchedule.status === 'pending' && (
            <Button
              onClick={() => {
                setRescheduleDialogOpen(true);
                setNewScheduleDate(selectedSchedule.scheduledAt.slice(0, 16));
              }}
            >
              Reschedule
            </Button>
          )}
          {selectedSchedule && selectedSchedule.status !== 'completed' && selectedSchedule.status !== 'cancelled' && (
            <Button
              color="error"
              onClick={() => {
                handleCancelSchedule(selectedSchedule.id);
                setSelectedSchedule(null);
              }}
            >
              Cancel
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Reschedule Dialog */}
      <Dialog
        open={rescheduleDialogOpen}
        onClose={() => {
          setRescheduleDialogOpen(false);
          setSelectedSchedule(null);
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reschedule Publication</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            type="datetime-local"
            label="New Schedule Time"
            value={newScheduleDate}
            onChange={(e) => setNewScheduleDate(e.target.value)}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setRescheduleDialogOpen(false);
              setSelectedSchedule(null);
            }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSaveReschedule}
            disabled={!newScheduleDate || updateMutation.isPending}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
