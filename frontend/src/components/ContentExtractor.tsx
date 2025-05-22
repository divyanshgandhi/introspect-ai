import { useState } from "react";
import { Button } from "@/components/ui/button";
import { processContent } from "@/lib/api";
import { UserContext as UserContextType } from "@/lib/api";
import { Loader2, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

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
  const hasContent = files.length > 0 || youtubeUrl !== "";

  const handleProcessContent = async () => {
    if (!hasContent) return;
    
    setIsLoading(true);
    setIsProcessing(true);
    setError(null);
    onProcess(); // Notify parent component
    
    try {
      // Select the first file if multiple files are uploaded
      const file = files.length > 0 ? files[0] : null;
      const url = youtubeUrl !== "" ? youtubeUrl : null;
      
      // Call the API
      const result = await processContent(file, url, userInfo);
      
      // Send the generated prompt to the parent component
      onContentProcessed(result.prompt);
      
      toast({
        title: "Content processed successfully",
        description: "Your personalized prompt is ready!",
      });
    } catch (error) {
      console.error("Error processing content:", error);
      
      // Show error message to the user
      const errorMessage = error instanceof Error ? error.message : "An unexpected error occurred";
      setError(errorMessage);
      
      toast({
        title: "Processing failed",
        description: "There was an error processing your content. Please try again.",
        variant: "destructive",
      });
      
      // Reset the processing state
      setIsProcessing(false);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleRetry = () => {
    setError(null);
    handleProcessContent();
  };
  
  return (
    <div className="mt-8 flex flex-col items-center w-full">
      {error && (
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
        disabled={!hasContent || isLoading}
        size="lg"
        className={`w-full md:w-auto px-8 py-6 text-lg ${
          hasContent && !isLoading ? "bg-primary hover:bg-primary/90" : ""
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
      
      {!hasContent && (
        <p className="text-sm text-muted-foreground mt-2">
          Add a YouTube link to continue
        </p>
      )}
    </div>
  );
};

export default ContentExtractor;
