import { useState } from "react";
import UploadPane from "@/components/UploadPane";
import OutputPane from "@/components/OutputPane";
import Header from "@/components/layout/Header";

const Index = () => {
  const [extractedContent, setExtractedContent] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleContentProcessed = (content: string) => {
    setExtractedContent(content);
    setIsProcessing(false);
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <div className="w-1/2 border-r border-border">
          <div className="h-full overflow-auto p-6">
            <UploadPane 
              onContentProcessed={handleContentProcessed} 
              setIsProcessing={setIsProcessing} 
            />
          </div>
        </div>
        <div className="w-1/2">
          <OutputPane 
            extractedContent={extractedContent} 
            isProcessing={isProcessing} 
          />
        </div>
      </div>
    </div>
  );
};

export default Index;
