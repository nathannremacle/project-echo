import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  Pagination,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { creatorAttributionService, VideoAttribution } from '../../services/creatorAttribution';
import { useState } from 'react';

interface CreatorVideosProps {
  creatorName: string;
  onVideoSelect?: (videoId: string) => void;
}

export default function CreatorVideos({ creatorName, onVideoSelect }: CreatorVideosProps) {
  const [page, setPage] = useState(1);
  const itemsPerPage = 20;

  const { data, isLoading } = useQuery({
    queryKey: ['creator-videos', creatorName, page],
    queryFn: () =>
      creatorAttributionService.getVideosByCreator(creatorName, itemsPerPage, (page - 1) * itemsPerPage),
  });

  const handlePageChange = (_: any, newPage: number) => {
    setPage(newPage);
  };

  if (isLoading) {
    return <Typography>Loading...</Typography>;
  }

  if (!data) {
    return <Typography>No data available</Typography>;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Videos by {creatorName}
        </Typography>

        <Box mb={2}>
          <Chip label={`${data.total} total video${data.total !== 1 ? 's' : ''}`} />
        </Box>

        <List>
          {data.videos.length === 0 ? (
            <ListItem>
              <ListItemText primary="No videos found" />
            </ListItem>
          ) : (
            data.videos.map((video: VideoAttribution) => (
              <ListItem
                key={video.id}
                button={!!onVideoSelect}
                onClick={() => onVideoSelect?.(video.id)}
              >
                <ListItemText
                  primary={video.source_title}
                  secondary={
                    <Box display="flex" gap={1} mt={0.5} flexWrap="wrap">
                      <Chip
                        label={video.publication_status}
                        size="small"
                        color={
                          video.publication_status === 'published'
                            ? 'success'
                            : video.publication_status === 'failed'
                            ? 'error'
                            : 'default'
                        }
                      />
                      {video.created_at && (
                        <Chip
                          label={new Date(video.created_at).toLocaleDateString()}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))
          )}
        </List>

        {data.total > itemsPerPage && (
          <Box display="flex" justifyContent="center" mt={2}>
            <Pagination
              count={Math.ceil(data.total / itemsPerPage)}
              page={page}
              onChange={handlePageChange}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
