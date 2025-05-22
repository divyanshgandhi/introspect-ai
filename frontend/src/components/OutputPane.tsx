import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Clipboard, CheckCheck } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

interface OutputPaneProps {
  extractedContent: string;
  isProcessing: boolean;
}

const OutputPane = ({ extractedContent, isProcessing }: OutputPaneProps) => {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);
  
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(extractedContent);
      setCopied(true);
      toast({
        title: "Copied to clipboard",
        description: "You can now paste this prompt into ChatGPT",
      });
      
      setTimeout(() => {
        setCopied(false);
      }, 3000);
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Please try again or copy manually",
        variant: "destructive",
      });
    }
  };
  
  return (
    <div className="h-full flex flex-col bg-background">
      <div className="flex justify-between items-center p-6 border-b border-border">
        <h2 className="text-2xl font-semibold">Your Personalized Prompt</h2>
        
        {extractedContent && (
          <Button 
            onClick={copyToClipboard}
            variant="outline"
            className="flex items-center gap-2"
            disabled={copied}
          >
            {copied ? (
              <>
                <CheckCheck size={16} />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Clipboard size={16} />
                <span>Copy</span>
              </>
            )}
          </Button>
        )}
      </div>
      
      <div className="flex-1 overflow-auto p-6">
        {isProcessing ? (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="w-16 h-16 border-4 border-primary border-t-primary/30 rounded-full animate-spin mb-4"></div>
            <p className="text-lg text-muted-foreground">Generating your personalized prompt...</p>
          </div>
        ) : extractedContent ? (
          <Card className="p-6 shadow-md border-border bg-card h-full overflow-auto whitespace-pre-wrap">
            <div className="prose max-w-none dark:prose-invert">
              {extractedContent.split("\n").map((line, index) => (
                <div key={index} className={line.trim().startsWith("Based on") ? "font-semibold mt-4" : ""}>
                  {line}
                  <br />
                </div>
              ))}
            </div>
          </Card>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="bg-primary/10 rounded-full p-6 mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                <path d="M14 2v6h6" />
                <path d="M16 13H8" />
                <path d="M16 17H8" />
                <path d="M10 9H8" />
              </svg>
            </div>
            <h3 className="text-xl font-medium mb-2">Your prompt will appear here</h3>
            <p className="text-muted-foreground max-w-md">
              Add a YouTube link and provide information about yourself to generate a personalized prompt for ChatGPT.
            </p>
          </div>
        )}
        
        {extractedContent && (
          <div className="mt-8 bg-primary/10 p-4 rounded-lg">
            <h3 className="font-medium mb-2">What's next?</h3>
            <p className="text-sm text-muted-foreground">
              Copy this prompt and paste it into ChatGPT to get your personalized plan. This prompt includes information about your content and context to help ChatGPT create recommendations tailored specifically to you.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default OutputPane;
