import { useState } from "react";
import { Button } from "@/components/ui/button";
import { processContent, RateLimitError } from "@/lib/api";
import { UserContext as UserContextType } from "@/lib/api";
import { Loader2, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useRateLimit } from "@/hooks/useRateLimit";
import RateLimitDisplay from "./RateLimitDisplay";

interface ContentExtractorProps {
  files: File[];
  youtubeUrl: string;
  userInfo: UserContextType;
  onProcess: () => void;
  onContentProcessed: (content: string) => void;
  setIsProcessing: (isProcessing: boolean) => void;
}

const ContentExtractor = ({ 
  files, 
  youtubeUrl, 
  userInfo,
  onProcess, 
  onContentProcessed,
  setIsProcessing
}: ContentExtractorProps) => {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRateLimited, setIsRateLimited] = useState(false);
  const { rateLimitStatus, refreshRateLimitStatus } = useRateLimit();
  
  const hasContent = files.length > 0 || youtubeUrl !== "";
  const isDisabled = !hasContent || isLoading || (rateLimitStatus?.remaining_requests === 0);

  const handleProcessContent = async () => {
    if (!hasContent) return;
    
    setIsLoading(true);
    setIsProcessing(true);
    setError(null);
    setIsRateLimited(false);
    onProcess(); // Notify parent component
    
    try {
      // Select the first file if multiple files are uploaded
      const file = files.length > 0 ? files[0] : null;
      const url = youtubeUrl !== "" ? youtubeUrl : null;
      
      // Call the API
      const result = await processContent(file, url, userInfo);
      
      // Send the generated prompt to the parent component
      onContentProcessed(result.prompt);
      
      // Refresh rate limit status after successful request
      refreshRateLimitStatus();
      
      toast({
        title: "Content processed successfully",
        description: "Your personalized prompt is ready!",
      });
    } catch (error) {
      console.error("Error processing content:", error);
      
      // Check if it's a rate limit error
      if (error instanceof Error && error.message.includes('Rate limit exceeded')) {
        setIsRateLimited(true);
        setError(null);
        
        toast({
          title: "Rate limit exceeded",
          description: "You have used all your free requests. Please contact @divyanshgandhi for more.",
          variant: "destructive",
        });
      } else {
        // Show other error messages to the user
        const errorMessage = error instanceof Error ? error.message : "An unexpected error occurred";
        setError(errorMessage);
        
        toast({
          title: "Processing failed",
          description: "There was an error processing your content. Please try again.",
          variant: "destructive",
        });
      }
      
      // Refresh rate limit status after any request (successful or failed)
      refreshRateLimitStatus();
      
      // Reset the processing state
      setIsProcessing(false);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleRetry = () => {
    setError(null);
    setIsRateLimited(false);
    handleProcessContent();
  };
  
  return (
    <div className="mt-8 flex flex-col items-center w-full">
      {error && !isRateLimited && (
        <Alert variant="destructive" className="mb-4 w-full">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error}
            <div className="mt-2">
              <Button variant="outline" size="sm" onClick={handleRetry}>
                Try Again
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}
      
      <Button
        onClick={handleProcessContent}
        disabled={isDisabled}
        size="lg"
        className={`w-full md:w-auto px-8 py-6 text-lg ${
          hasContent && !isLoading && !isDisabled ? "bg-primary hover:bg-primary/90" : ""
        }`}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          "Generate Personalized Prompt"
        )}
      </Button>
      
      {/* Rate limit display */}
      <RateLimitDisplay 
        rateLimitStatus={rateLimitStatus}
        isRateLimited={isRateLimited}
      />
      
      {!hasContent && !isRateLimited && (
        <p className="text-sm text-muted-foreground mt-2">
          Add a YouTube link to continue
        </p>
      )}
    </div>
  );
};

export default ContentExtractor;
