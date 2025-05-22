import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { Play } from "lucide-react";

interface YouTubeInputProps {
  onUrlChange: (url: string) => void;
}

const YouTubeInput = ({ onUrlChange }: YouTubeInputProps) => {
  const { toast } = useToast();
  const [url, setUrl] = useState("");
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null);
  const [videoId, setVideoId] = useState<string | null>(null);
  const [videoTitle, setVideoTitle] = useState<string | null>(null);
  const [channelName, setChannelName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const validateUrl = (url: string): boolean => {
    // Simple YouTube URL validation
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    return youtubeRegex.test(url);
  };

  const extractVideoId = (url: string): string | null => {
    const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[7].length === 11) ? match[7] : null;
  };

  // Fetch video metadata using oEmbed API
  const fetchVideoMetadata = async (videoId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`
      );
      
      if (response.ok) {
        const data = await response.json();
        setVideoTitle(data.title);
        setChannelName(data.author_name);
      } else {
        setVideoTitle(null);
        setChannelName(null);
      }
    } catch (error) {
      console.error("Error fetching video metadata:", error);
      setVideoTitle(null);
      setChannelName(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Update the URL and validation whenever input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setUrl(newUrl);
    
    if (newUrl.trim() === "") {
      setIsValid(null);
      setThumbnailUrl(null);
      setVideoId(null);
      setVideoTitle(null);
      setChannelName(null);
      onUrlChange(""); // Clear the URL
      return;
    }
    
    const valid = validateUrl(newUrl);
    setIsValid(valid);
    
    if (valid) {
      const extractedVideoId = extractVideoId(newUrl);
      if (extractedVideoId) {
        setVideoId(extractedVideoId);
        setThumbnailUrl(`https://img.youtube.com/vi/${extractedVideoId}/0.jpg`);
        fetchVideoMetadata(extractedVideoId);
        onUrlChange(newUrl); // Pass the valid URL to parent immediately
      }
    } else {
      setThumbnailUrl(null);
      setVideoId(null);
      setVideoTitle(null);
      setChannelName(null);
    }
  };

  // Handle form submission (now just prevents default)
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
  };

  const openYoutubeVideo = () => {
    if (videoId) {
      window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank');
    }
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Input
            type="text"
            placeholder="Paste YouTube URL here"
            value={url}
            onChange={handleInputChange}
            className={`${
              isValid === false ? "border-destructive" : 
              isValid === true ? "border-primary" : ""
            }`}
          />
          {isValid === false && (
            <p className="text-sm text-destructive">Please enter a valid YouTube URL</p>
          )}
        </div>
      </form>
      
      {thumbnailUrl && (
        <div className="mt-4">
          <p className="text-sm font-medium mb-2">Video Preview:</p>
          <div 
            className="relative aspect-video bg-card rounded-lg overflow-hidden group cursor-pointer"
            onClick={openYoutubeVideo}
            title="Click to play video"
          >
            <img 
              src={thumbnailUrl} 
              alt="YouTube thumbnail" 
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-black/40 flex items-center justify-center group-hover:bg-black/60 transition-all">
              <div className="w-20 h-20 rounded-full bg-red-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <Play size={32} fill="white" className="ml-1" />
              </div>
            </div>
          </div>
          
          {/* Video metadata display */}
          <div className="mt-2 space-y-1">
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading video information...</p>
            ) : (
              <>
                {videoTitle && (
                  <p className="text-sm font-semibold line-clamp-2">{videoTitle}</p>
                )}
                {channelName && (
                  <p className="text-xs text-muted-foreground">{channelName}</p>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default YouTubeInput;
