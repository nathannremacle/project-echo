import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Box,
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { ChannelStatisticsWithTrends } from '../../services/statistics';

interface ChannelBreakdownProps {
  channels: Array<{
    id: string;
    name: string;
    statistics: ChannelStatisticsWithTrends;
  }>;
}

export default function ChannelBreakdown({ channels }: ChannelBreakdownProps) {
  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Per-Channel Breakdown
        </Typography>
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Channel</TableCell>
                <TableCell align="right">Subscribers</TableCell>
                <TableCell align="right">Total Views</TableCell>
                <TableCell align="right">Videos</TableCell>
                <TableCell align="right">Growth</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {channels.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No channel data available
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                channels.map((channel) => {
                  const { current, trends } = channel.statistics;
                  const subscriberGrowth = trends.subscriberGrowth || 0;
                  const viewGrowth = trends.viewGrowth || 0;

                  return (
                    <TableRow key={channel.id}>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {channel.name}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                          <Typography variant="body2">{formatNumber(current.subscriberCount)}</Typography>
                          {subscriberGrowth !== 0 && (
                            <Box display="flex" alignItems="center" gap={0.5}>
                              {subscriberGrowth >= 0 ? (
                                <TrendingUp fontSize="small" color="success" />
                              ) : (
                                <TrendingDown fontSize="small" color="error" />
                              )}
                              <Typography
                                variant="caption"
                                color={subscriberGrowth >= 0 ? 'success.main' : 'error.main'}
                              >
                                {subscriberGrowth >= 0 ? '+' : ''}{subscriberGrowth.toFixed(1)}%
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                          <Typography variant="body2">{formatNumber(current.totalViews)}</Typography>
                          {viewGrowth !== 0 && (
                            <Box display="flex" alignItems="center" gap={0.5}>
                              {viewGrowth >= 0 ? (
                                <TrendingUp fontSize="small" color="success" />
                              ) : (
                                <TrendingDown fontSize="small" color="error" />
                              )}
                              <Typography
                                variant="caption"
                                color={viewGrowth >= 0 ? 'success.main' : 'error.main'}
                              >
                                {viewGrowth >= 0 ? '+' : ''}{viewGrowth.toFixed(1)}%
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">{current.totalVideos}</Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={subscriberGrowth >= 0 ? 'Growing' : 'Declining'}
                          color={subscriberGrowth >= 0 ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}
