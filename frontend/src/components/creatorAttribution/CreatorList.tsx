import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  TextField,
  InputAdornment,
  Chip,
  Button,
} from '@mui/material';
import { Search, Download } from '@mui/icons-material';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { creatorAttributionService, Creator } from '../../services/creatorAttribution';

interface CreatorListProps {
  onCreatorSelect?: (creatorName: string) => void;
}

export default function CreatorList({ onCreatorSelect }: CreatorListProps) {
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch all creators
  const { data: allCreators, isLoading: isLoadingAll } = useQuery({
    queryKey: ['creators-list'],
    queryFn: () => creatorAttributionService.listCreators(),
  });

  // Search creators
  const { data: searchResults, isLoading: isLoadingSearch } = useQuery({
    queryKey: ['creators-search', searchQuery],
    queryFn: () => creatorAttributionService.searchCreators(searchQuery, 50),
    enabled: searchQuery.length > 0,
  });

  const creators = searchQuery.length > 0 ? searchResults?.creators || [] : allCreators?.creators || [];
  const isLoading = searchQuery.length > 0 ? isLoadingSearch : isLoadingAll;

  const handleExport = async () => {
    try {
      const data = await creatorAttributionService.exportCreators('json');
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `creators-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export creators:', error);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Creators</Typography>
          <Button
            variant="outlined"
            size="small"
            startIcon={<Download />}
            onClick={handleExport}
          >
            Export
          </Button>
        </Box>

        <TextField
          fullWidth
          placeholder="Search creators..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />

        {isLoading ? (
          <Typography>Loading...</Typography>
        ) : (
          <List>
            {creators.length === 0 ? (
              <ListItem>
                <ListItemText primary="No creators found" />
              </ListItem>
            ) : (
              creators.map((creator: Creator) => (
                <ListItem
                  key={creator.name}
                  button={!!onCreatorSelect}
                  onClick={() => onCreatorSelect?.(creator.name)}
                >
                  <ListItemText
                    primary={creator.name}
                    secondary={
                      <Box display="flex" gap={1} mt={0.5}>
                        <Chip
                          label={`${creator.video_count} video${creator.video_count !== 1 ? 's' : ''}`}
                          size="small"
                        />
                      </Box>
                    }
                  />
                </ListItem>
              ))
            )}
          </List>
        )}
      </CardContent>
    </Card>
  );
}
